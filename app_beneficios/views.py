from django.shortcuts import render, get_object_or_404, redirect
from .models import ControleBeneficioModel, BeneficioModel, ControleBeneficioHistoricoModel
from django.db.models import Q, F
from django.db import transaction
from .forms import ControleBeneficioForm, BeneficioModelForm
from .models import UF_CHOICES  # Import UF_CHOICES from the models
from django.contrib import messages
from django.views.generic import CreateView, ListView, DetailView
from django.views.generic.edit import FormMixin
from .utils import upload_to_drive
from .utils import criar_leva # Importa a função criar_leva
import os
from django.views.generic import TemplateView
from django.views import View
from django.urls import reverse, reverse_lazy

from accounts.mixins import GroupPermissionRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils import timezone
from collections import OrderedDict
from datetime import date
from collections import OrderedDict
from app_associados.models import AssociadoModel
from django.db import transaction
from django.contrib.auth.decorators import login_required, permission_required
from app_documentos.models import Documento, TipoDocumentoModel  # certifique-se de importar corretamente
from .models import LevaProcessamentoBeneficio, ControleLevaItem  # Import the required models
from django.contrib.auth.models import User  # Import User model
from django.http import Http404  # Import Http404 for raising 404 errors
from django.db.models import Q


# Benefícios Cadastrados - Lista dos benefícios Lançados 
class BeneficioListView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = BeneficioModel
    template_name = 'app_beneficios/beneficios.html'
    context_object_name = 'beneficios'
    ordering = ['-ano_concessao', 'nome', 'estado']
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        beneficios = self.get_queryset()
        beneficios_com_leva = []

        for beneficio in beneficios:
            leva = LevaProcessamentoBeneficio.objects.filter(
                beneficio=beneficio
            ).order_by('-criado_em').first()

            if leva:
                # Itens livres (qualquer um pode pegar)
                itens_pendentes = leva.itens.filter(status='PENDENTE')

                # Itens que foram pausados pelo usuário atual
                meus_pausados = leva.itens.filter(
                    status='PENDENTE',
                    atualizado_por=self.request.user
                )

                # Itens que estou processando
                meus_em_processamento = leva.itens.filter(
                    status='PROCESSANDO',
                    em_processamento_por=self.request.user
                )

                if itens_pendentes.exists():
                    proximo_item = itens_pendentes.order_by(
                        'controle_beneficio__associado__user__first_name',
                        'controle_beneficio__associado__user__last_name'
                    ).first()

                elif meus_em_processamento.exists():
                    proximo_item = meus_em_processamento.order_by(
                        'controle_beneficio__associado__user__first_name',
                        'controle_beneficio__associado__user__last_name'
                    ).first()

                elif meus_pausados.exists():
                    proximo_item = meus_pausados.order_by(
                        'controle_beneficio__associado__user__first_name',
                        'controle_beneficio__associado__user__last_name'
                    ).first()
                else:
                    proximo_item = None

                usuarios_processando = User.objects.filter(
                    processando_itens__leva=leva,
                    processando_itens__status='PROCESSANDO'
                ).distinct()

                # 🔥 Total para este usuário
                total_para_este_usuario = itens_pendentes.count()

                if not itens_pendentes.exists() and meus_pausados.exists():
                    total_para_este_usuario = meus_pausados.count()

                itens_concluidos = leva.itens.filter(status='CONCLUIDO').count()
                itens_em_processamento = leva.itens.filter(status='PROCESSANDO').count()

                beneficios_com_leva.append({
                    'beneficio': beneficio,
                    'leva': leva,
                    'proximo_item': proximo_item,
                    'usuarios_processando': usuarios_processando,
                    'tem_meu_pausado': meus_pausados.exists(),
                    'tem_pendentes': itens_pendentes.exists(),
                    'total_para_este_usuario': total_para_este_usuario,
                    'quantidade_pendentes': itens_pendentes.count(),
                    'quantidade_concluidos': itens_concluidos,
                    'quantidade_em_processamento': itens_em_processamento,
                    'total_itens': itens_pendentes.count() + itens_em_processamento + itens_concluidos,
                })

            else:
                # 🔥 Caso não tenha leva
                beneficios_com_leva.append({
                    'beneficio': beneficio,
                    'leva': None,
                    'proximo_item': None,
                    'usuarios_processando': [],
                    'tem_meu_pausado': False,
                    'tem_pendentes': False,
                    'total_para_este_usuario': 0,
                })

        context['beneficios_com_leva'] = beneficios_com_leva
        return context

    
# Controle - Listagem controle de benefícios - Associados e Estados
class ListaBeneficiosView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = ControleBeneficioModel
    template_name = 'app_beneficios/list_beneficios.html'
    context_object_name = 'controles'

    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]

    def get_queryset(self):
        queryset = ControleBeneficioModel.objects.select_related(
            'beneficio', 'associado__user'
        )

        # 🔎 Filtros
        beneficio_filtro = self.request.GET.get('beneficio')
        status = self.request.GET.get('status')
        nome_associado = self.request.GET.get('nome_associado')

        if beneficio_filtro:
            partes = beneficio_filtro.split('__')
            nome = partes[0]
            ano = partes[1] if len(partes) > 1 else None
            estado = partes[2] if len(partes) > 2 else None

            queryset = queryset.filter(beneficio__nome=nome)
            if ano:
                queryset = queryset.filter(beneficio__ano_concessao=ano)
            if estado:
                queryset = queryset.filter(beneficio__estado=estado)

        if status:
            queryset = queryset.filter(status_pedido=status)

        if nome_associado:
            queryset = queryset.filter(
                Q(associado__user__first_name__icontains=nome_associado) |
                Q(associado__user__last_name__icontains=nome_associado)
            )

        return queryset.order_by(
            'associado__user__first_name', 'associado__user__last_name'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 🔥 Agrupar benefícios disponíveis
        beneficios_agrupados = {}
        for beneficio in BeneficioModel.objects.order_by('-ano_concessao', 'nome'):
            if beneficio.nome not in beneficios_agrupados:
                beneficios_agrupados[beneficio.nome] = []
            beneficios_agrupados[beneficio.nome].append(beneficio)

        context.update({
            'beneficios_agrupados': beneficios_agrupados,
            'status_choices': ControleBeneficioModel._meta.get_field('status_pedido').choices,
            'uf_choices': UF_CHOICES,
            'nome_associado': self.request.GET.get('nome_associado', ''),
        })
        return context


# Controle de Beneficios - Detalhes do benefício e dados do associado / Automação
class ControleBeneficioDetailView(LoginRequiredMixin, GroupPermissionRequiredMixin, FormMixin, DetailView):
    model = ControleBeneficioModel
    form_class = ControleBeneficioForm
    template_name = 'app_beneficios/controle_detail.html'
    context_object_name = 'controle'
    success_url = reverse_lazy('app_beneficios:lista_beneficios')

    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]

    def get_success_url(self):
        return reverse_lazy('app_beneficios:controle_detalhe', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        return form_class(instance=self.get_object(), **self.get_form_kwargs())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            controle = form.save(commit=False)
            controle._current_user = request.user
            controle.save()
            messages.success(request, "✅ Registro atualizado com sucesso!")
            return redirect(self.get_success_url())
        else:
            messages.error(request, "⚠️ Erro ao salvar. Verifique os campos.")
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        controle = self.get_object()

        # 👇 Aqui é a flag principal
        veio_da_leva = self.request.GET.get('pela_leva') == '1'
    
        tipos_desejados = [
            'RG', 'RGP', 'NIT', 'CPF', 'CNH', 'CEI',
            'Comprovante Residência', 'Declaração Residência - MAPA',
            'Foto3x4', 'CAEPF'
        ]

        tipos = TipoDocumentoModel.objects.filter(tipo__in=tipos_desejados)

        documentos_relevantes = Documento.objects.filter(
            associado=controle.associado,
            tipo_doc__in=tipos
        ).order_by('-data_upload')

        # 🔍 Pega diretamente o item dessa leva vinculado ao controle
        leva_item = ControleLevaItem.objects.filter(controle_beneficio=controle).first()


        if leva_item:
            leva = leva_item.leva
            pertence_a_leva = True

            itens_ordenados = leva.itens.order_by(
                'controle_beneficio__associado__user__first_name',
                'controle_beneficio__associado__user__last_name',
                'id'
            )

            lista_ids = list(itens_ordenados.values_list('id', flat=True))

            try:
                indice_atual = lista_ids.index(leva_item.id) + 1
            except ValueError:
                indice_atual = None

            itens_pendentes = leva.itens.filter(status='PENDENTE').count()
            itens_concluidos = leva.itens.filter(status='CONCLUIDO').count()

            itens_em_processamento = leva.itens.filter(status='PROCESSANDO').count()
            usuarios_processando = User.objects.filter(
                processando_itens__leva=leva,
                processando_itens__status='PROCESSANDO'
            ).distinct()

            total_itens = itens_pendentes + itens_em_processamento + itens_concluidos

            context.update({
                'leva': leva,
                'indice_atual': indice_atual,
                'total_itens': total_itens,
                'itens_concluidos': itens_concluidos,
                'itens_pendentes': itens_pendentes,
                'itens_em_processamento': itens_em_processamento,
                'total_a_fazer': itens_pendentes + itens_em_processamento,
                'usuarios_processando': usuarios_processando,
                'pertence_a_leva': pertence_a_leva,
                'pertence_a_leva': veio_da_leva, 
            })
        else:
            context.update({
                'leva': None,
                'pertence_a_leva': False,
            })

        context.update({
            'form': self.get_form(),
            'historico': controle.historico.all().order_by('-alterado_em'),
            'documentos_relevantes': documentos_relevantes,
            'associado': controle.associado,
        })

        return context

            

# Função Aplicar/Distribuir Benefícios - Associados
@login_required
def aplicar_beneficios_para_associado(request, associado_id):
    associado = get_object_or_404(AssociadoModel, id=associado_id)
    beneficios_ativos = BeneficioModel.objects.filter(
        data_inicio__lte=date.today(),
        data_fim__gte=date.today(),
    )

    criados = 0
    ignorados = 0

    for beneficio in beneficios_ativos:
        campo_esperado = f"recebe_{beneficio.nome}"

        # ✅ Só aplica se UF do município do associado for igual à UF do benefício
        if associado.municipio_circunscricao and associado.municipio_circunscricao.uf != beneficio.estado:
            continue

        if hasattr(associado, campo_esperado) and getattr(associado, campo_esperado) == 'Recebe':
            if not ControleBeneficioModel.objects.filter(associado=associado, beneficio=beneficio).exists():
                ControleBeneficioModel.objects.create(
                    associado=associado,
                    beneficio=beneficio,
                    status_pedido='EM_PREPARO'
                )
                criados += 1
            else:
                ignorados += 1

    if criados:
        messages.success(request, f"{criados} benefício(s) aplicado(s) com sucesso.")
    elif ignorados:
        messages.info(request, "Todos os benefícios já estavam aplicados.")
    else:
        messages.warning(request, "Nenhum benefício foi aplicado. Verifique a UF do benefício e se o associado está marcado como 'Recebe'.")

    return redirect('app_associados:single_associado', associado_id)


# Seleciona associados aptos ao lançamento do benefício por estado/associação/repartição/ano
@login_required
def escolher_beneficio_para_associado(request, associado_id):
    associado = get_object_or_404(AssociadoModel, id=associado_id)

    # Filtra benefícios do ano vigente
    ano = date.today().year
    beneficios = BeneficioModel.objects.filter(ano_concessao=ano)

    # Aplica lógica de aptidão por campo
    aplicaveis = []
    for beneficio in beneficios:
        campo = f"recebe_{beneficio.nome}"
        if hasattr(associado, campo) and getattr(associado, campo) == 'Recebe':
            if not ControleBeneficioModel.objects.filter(associado=associado, beneficio=beneficio).exists():
                aplicaveis.append(beneficio)

    if request.method == "POST":
        beneficio_id = request.POST.get("beneficio_id")
        beneficio = get_object_or_404(BeneficioModel, id=beneficio_id)

        ControleBeneficioModel.objects.create(
            associado=associado,
            beneficio=beneficio,
            status_pedido='EM_PREPARO'
        )
        messages.success(request, f"Benefício '{beneficio.get_nome_display()}' aplicado com sucesso.")
        return redirect('app_associados:single_associado', associado.id)

    return render(request, 'app_beneficios/aplicar_beneficio_para_associado.html', {
        'associado': associado,
        'beneficios': aplicaveis,
    })


# Painel de Visualização de Benefícios - Colunas Status
class PainelBeneficiosView(LoginRequiredMixin, GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_beneficios/painel_beneficios.html'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter as choices do modelo
        status_choices = ControleBeneficioModel.STATUS_CHOICES
        etapas_beneficios = [choice[0] for choice in status_choices]
        
        # Filtro por benefício (se especificado)
        beneficio_filtro = self.request.GET.get('beneficio')
        
        # Query base - controles de benefício
        controles = ControleBeneficioModel.objects.select_related(
            'associado__user', 'beneficio'
        ).order_by('-atualizado_em')
        
        # Aplicar filtro se existir
        if beneficio_filtro:
            partes = beneficio_filtro.split('__')
            nome = partes[0]
            
            # Verificar se tem ano e estado
            if len(partes) >= 2:
                ano = partes[1]
                controles = controles.filter(beneficio__ano_concessao=ano)
            else:
                ano = None
            
            if len(partes) >= 3:
                estado = partes[2]
                controles = controles.filter(beneficio__estado=estado)
            else:
                estado = None
            
            controles = controles.filter(beneficio__nome=nome)
        
        # Agrupar por status
        def agrupar_por_status(queryset, etapas):
            grupos = OrderedDict()
            for etapa in etapas:
                grupos[etapa] = []
            
            for controle in queryset:
                if controle.status_pedido in grupos:
                    grupos[controle.status_pedido].append(controle)
            
            return grupos
        
        # Benefícios disponíveis para filtro (agrupados por nome)
        todos_beneficios = BeneficioModel.objects.all().order_by('nome', '-ano_concessao', 'estado')
        
        # Agrupar benefícios por nome para o template
        beneficios_agrupados = {}
        for beneficio in todos_beneficios:
            if beneficio.nome not in beneficios_agrupados:
                beneficios_agrupados[beneficio.nome] = []
            beneficios_agrupados[beneficio.nome].append(beneficio)
        
        # Adicionar ao contexto
        context.update({
            'painel_beneficios': agrupar_por_status(controles, etapas_beneficios),
            'status_labels': dict(status_choices),
            'beneficios_agrupados': beneficios_agrupados,
            'beneficio_selecionado': beneficio_filtro,
            'uf_choices': UF_CHOICES  # Certifique-se de importar UF_CHOICES
        })
        
        return context

# Create Benefício - Formulário de Cadastro
class AdicionarBeneficioView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = BeneficioModel
    form_class = BeneficioModelForm
    template_name = 'app_beneficios/create_beneficio.html'
    success_url = reverse_lazy('app_beneficios:lista_beneficios')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]    

    def form_valid(self, form):
        messages.success(self.request, "✅ Benefício cadastrado com sucesso!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "⚠️ Erro ao cadastrar. Verifique os campos.")
        return super().form_invalid(form)


# Lista e Edita Benefícios - Formulário de Edição
class ListaEditaBeneficiosView(GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_beneficios/edit_beneficio.html'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]

    def get(self, request, *args, **kwargs):
        beneficio_id = request.GET.get('id')
        beneficio_editando = None

        if beneficio_id:
            beneficio_editando = get_object_or_404(BeneficioModel, pk=beneficio_id)
            form = BeneficioModelForm(instance=beneficio_editando, modo_edicao=True)
        else:
            form = BeneficioModelForm()

        context = self.get_context_data(**kwargs)
        context.update({
            'beneficios': BeneficioModel.objects.order_by('-ano_concessao', 'nome'),
            'form': form,
            'beneficio_editando': beneficio_editando,
        })
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        beneficio_id = request.POST.get('beneficio_id')
        beneficio = get_object_or_404(BeneficioModel, pk=beneficio_id)
        form = BeneficioModelForm(request.POST, instance=beneficio, modo_edicao=True)
        beneficio_editando = beneficio

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"✅ Benefício '{beneficio.get_nome_display()}' atualizado com sucesso!"
            )
            return redirect(reverse_lazy('app_beneficios:beneficios'))
        else:
            messages.error(
                request,
                "⚠️ Erro ao salvar os dados. Verifique os campos."
            )

        context = self.get_context_data(**kwargs)
        context.update({
            'beneficios': BeneficioModel.objects.order_by('-ano_concessao', 'nome'),
            'form': form,
            'beneficio_editando': beneficio_editando,
        })
        return self.render_to_response(context)




@login_required
@permission_required('app_beneficios.delete_beneficiomodel', raise_exception=True)
def deletar_beneficio(request, pk):
    beneficio = get_object_or_404(BeneficioModel, pk=pk)

    nome_display = beneficio.get_nome_display()
    ano = beneficio.ano_concessao
    estado = beneficio.estado

    beneficio.delete()  # 💣 Deleta em cascata os registros vinculados

    messages.success(request, f"🗑️ Benefício '{nome_display} ({ano}/{estado})' deletado com sucesso!")
    return redirect('app_beneficios:beneficios')


# Leva de Processamento de Benefícios - Criação
@login_required
def criar_leva_view(request, beneficio_id):
    beneficio = get_object_or_404(BeneficioModel, pk=beneficio_id)

    # 🔍 Busca leva existente com base exata no benefício (não por nome/ano/estado isolados)
    leva_existente = LevaProcessamentoBeneficio.objects.filter(
        beneficio=beneficio
    ).order_by('-criado_em').first()

    if leva_existente:
        # ⚠️ Se houver itens pendentes ou em processamento, redirecionar
        if leva_existente.itens.filter(status__in=['PENDENTE', 'PROCESSANDO']).exists():
            itens_pendentes = leva_existente.itens.filter(status='PENDENTE')
            itens_em_processamento = leva_existente.itens.filter(
                status='PROCESSANDO',
                em_processamento_por=request.user
            )

            if itens_pendentes.exists():
                proximo_item = itens_pendentes.order_by(
                    'controle_beneficio__associado__user__first_name',
                    'controle_beneficio__associado__user__last_name'
                ).first()
                return redirect('app_beneficios:processar_item_leva', item_id=proximo_item.id)

            elif itens_em_processamento.exists():
                proximo_item = itens_em_processamento.order_by(
                    'controle_beneficio__associado__user__first_name',
                    'controle_beneficio__associado__user__last_name'
                ).first()
                return redirect('app_beneficios:processar_item_leva', item_id=proximo_item.id)

            else:
                messages.info(request, "⚠️ Esta leva não possui itens pendentes.")
                return redirect('app_beneficios:lista_beneficios')

    # 🚀 Criar nova leva se nenhuma ativa foi encontrada
    nova_leva = criar_leva(beneficio, request.user)

    if not nova_leva.itens.exists():
        messages.warning(request, "⚠️ Nenhum item foi criado na nova leva.")
        return redirect('app_beneficios:lista_beneficios')

    primeiro_item = nova_leva.itens.filter(status='PENDENTE').order_by(
        'controle_beneficio__associado__user__first_name',
        'controle_beneficio__associado__user__last_name'
    ).first()

    if primeiro_item:
        return redirect('app_beneficios:processar_item_leva', item_id=primeiro_item.id)

    # 🔁 Fallback final
    messages.warning(request, "⚠️ A leva foi criada, mas não há itens prontos para processar.")
    return redirect('app_beneficios:lista_beneficios')


# Leva de Processamento de Benefícios - Listagem
class ProcessarLevaItemView(LoginRequiredMixin, GroupPermissionRequiredMixin, FormMixin, DetailView):
    model = ControleLevaItem
    form_class = ControleBeneficioForm
    template_name = 'app_beneficios/controle_detail.html'
    context_object_name = 'item'

    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]

    # ✅ Garante que o item existe e pertence corretamente à leva
    def get_object(self, queryset=None):
        item = get_object_or_404(ControleLevaItem, id=self.kwargs.get('item_id'))

        if not item.leva:
            raise Http404("❌ Este item não pertence a nenhuma leva ativa.")

        if item.status == 'PENDENTE':
            item.status = 'PROCESSANDO'
            item.em_processamento_por = self.request.user
            item.atualizado_por = self.request.user
            item.save()

        elif item.status == 'PROCESSANDO':
            if item.em_processamento_por != self.request.user:
                messages.error(
                    self.request,
                    f"⚠️ Este item está sendo processado por {item.em_processamento_por.get_full_name()}."
                )
                raise Http404("Item em processamento por outro usuário.")

        elif item.status == 'CONCLUIDO':
            messages.info(
                self.request,
                "✅ Este item já foi concluído. Indo para o próximo..."
            )
            raise Http404("Item já concluído.")

        return item


    def get_success_url(self):
        leva = self.object.leva

        itens_ordenados = leva.itens.order_by(
            'controle_beneficio__associado__user__first_name',
            'controle_beneficio__associado__user__last_name',
            'id'
        )

        itens_restantes = itens_ordenados.filter(status='PENDENTE')

        if itens_restantes.exists():
            proximo_item = itens_restantes.first()
            return reverse('app_beneficios:processar_item_leva', kwargs={'item_id': proximo_item.id})

        itens_em_processamento = itens_ordenados.filter(
            status='PROCESSANDO',
            em_processamento_por=self.request.user
        )

        if itens_em_processamento.exists():
            return reverse('app_beneficios:processar_item_leva', kwargs={'item_id': itens_em_processamento.first().id})

        messages.info(self.request, "🎉 Todos os itens desta leva foram processados.")
        return reverse('app_beneficios:lista_beneficios')
    
    def dispatch(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, "❌ Item não encontrado ou já foi concluído.")
            return redirect('app_beneficios:lista_beneficios')
        return super().dispatch(request, *args, **kwargs)



    # ✅ Form padrão
    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        if not self.object:
            raise Http404("❌ Item não encontrado.")
        return form_class(
            instance=self.object.controle_beneficio,
            **self.get_form_kwargs()
        )


    # ✅ Ações dos botões
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            controle = form.save(commit=False)
            controle._current_user = request.user
            controle.save()

            acao = request.POST.get('acao')

            if acao == 'salvar_proximo':
                self.object.status = 'CONCLUIDO'
                self.object.em_processamento_por = None
                self.object.atualizado_por = request.user
                self.object.save()

                return redirect(self.get_success_url())  # 👉 Aqui pega o próximo item

            elif acao == 'salvar_pausar':
                self.object.status = 'PENDENTE'
                self.object.em_processamento_por = None
                self.object.atualizado_por = request.user
                self.object.save()

                messages.info(request, "⏸️ Processamento pausado.")
                return redirect('app_beneficios:lista_beneficios')

            elif acao == 'salvar_continuar':
                self.object.status = 'PROCESSANDO'
                self.object.em_processamento_por = request.user
                self.object.atualizado_por = request.user
                self.object.save()

                messages.success(request, "✅ Alterações salvas. Continue editando.")


            if 'pela_leva' in request.GET:
                return redirect(
                    reverse('app_beneficios:controle_detalhe', kwargs={'pk': self.object.controle_beneficio.id})
                    + '?pela_leva=1'
                )
            else:
                return redirect('app_beneficios:controle_detalhe', kwargs={'pk': self.object.controle_beneficio.id})

                
        messages.error(request, "⚠️ Erro ao salvar. Verifique os campos.")
        return self.form_invalid(form)

    # ✅ Dados do contexto para template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        controle = self.object.controle_beneficio
        leva = self.object.leva

        itens_ordenados = leva.itens.order_by(
            'controle_beneficio__associado__user__first_name',
            'controle_beneficio__associado__user__last_name',
            'id'
        )

        lista_ids = list(itens_ordenados.values_list('controle_beneficio_id', flat=True))

        if self.object.controle_beneficio_id not in lista_ids:
            messages.error(self.request, "❌ Este controle não pertence à leva atual.")
            raise Http404("Controle não encontrado na leva.")

        indice_atual = lista_ids.index(self.object.controle_beneficio_id)


        itens_pendentes = leva.itens.filter(status='PENDENTE').count()
        itens_em_processamento = leva.itens.filter(
            status='PROCESSANDO',
            controle_beneficio__isnull=False,
            em_processamento_por__isnull=False
        ).count()
        itens_concluidos = leva.itens.filter(status='CONCLUIDO').count()

        usuarios_processando = User.objects.filter(
            processando_itens__leva=leva,
            processando_itens__status='PROCESSANDO'
        ).distinct()

        total_itens = itens_pendentes + itens_em_processamento + itens_concluidos

        tipos_desejados = [
            'RG', 'RGP', 'NIT', 'CPF', 'CNH', 'CEI',
            'Comprovante Residência', 'Declaração Residência - MAPA',
            'Foto3x4', 'CAEPF'
        ]

        tipos = TipoDocumentoModel.objects.filter(tipo__in=tipos_desejados)

        documentos_relevantes = Documento.objects.filter(
            associado=controle.associado,
            tipo_doc__in=tipos
        ).order_by('-data_upload')

        leva_item = ControleLevaItem.objects.filter(controle_beneficio=self.object.controle_beneficio).first()


        context.update({
            'form': self.get_form(),
            'controle': controle,
            'historico': controle.historico.all().order_by('-alterado_em'),
            'documentos_relevantes': documentos_relevantes,
            'associado': controle.associado,
            'item': self.object,
            'leva': leva,
            'indice_atual': indice_atual,
            'total_itens': total_itens,
            'itens_concluidos': itens_concluidos,
            'itens_pendentes': itens_pendentes,
            'itens_em_processamento': itens_em_processamento,
            'total_a_fazer': itens_pendentes + itens_em_processamento,
            'usuarios_processando': usuarios_processando,
            'pertence_a_leva': leva_item is not None,
        })

        return context


