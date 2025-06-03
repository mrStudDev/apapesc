from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.forms.models import model_to_dict
from .models import ExtraAssociadoModel, ServicoHistoricoModel, ServicoAssociadoModel, ServicoExtraAssociadoModel
from app_associados.models import AssociadoModel
from app_associacao.models import ReparticoesModel, AssociacaoModel
from app_finances.forms import EntradaFinanceiraForm, TipoServicoModel
from .forms import ServicoAssociadoForm, ServicoExtraAssociadoForm , ExtraAssociadoForm
from django.contrib import messages
from urllib.parse import urlencode
from itertools import chain
from collections import defaultdict
from django.db.models import Q, Value, CharField
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import GroupPermissionRequiredMixin

# Logging
import logging


logger = logging.getLogger(__name__)


# SEVIÇOS
# Single Serviço - ASSOCIADO
from app_documentos.models import Documento, TipoDocumentoModel

class SingleServicoView(LoginRequiredMixin, GroupPermissionRequiredMixin, DetailView):
    model = ServicoAssociadoModel
    template_name = 'app_servicos/single_servico_associado.html'
    context_object_name = 'servico'
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
        servico = self.get_object()
        associado = servico.associado

        context.update({
            "historico": servico.historico.select_related("alterado_por").order_by("-data_alteracao") if hasattr(servico, 'historico') else [],
        })

        # Tipos relevantes: RG, RGP, NIT
        tipos_desejados = [
            'RG', 'RGP', 'NIT', 'CPF', 'CNH', 'CPF', 'TIE', 'CEI', 'CAEPF', 'Foto3x4', 
            'Comprovante Residência', 'Declaração Residência - MAPA',
            'Auto Declaração', 'Autorização de Acesso Gov Assinada',
            'Autorização de Uso de Imagem Assinada', 'Comprovante Seguro Defeso',
            'Ficha de Requerimento de Filiação Assinada', 'Título Eleitor',
            'Procuração Individual Ad Judicia Assinada', 'Procuração Individual Administrativa Assinada',
            'Licença Embarcação(Pesca)', 'Seguro DPEM', 'Protocolo RGP',
            
        ]
        tipos = TipoDocumentoModel.objects.filter(tipo__in=tipos_desejados)

        # Busca documentos do associado com esses tipos
        documentos_relevantes = Documento.objects.filter(
            associado=associado,
            tipo_doc__in=tipos
        ).order_by('-data_upload')

        context["documentos_relevantes"] = documentos_relevantes

        return context


# Single Serviço - EXTRAASSOCIADO
class ServicoExtraDetailView(LoginRequiredMixin, GroupPermissionRequiredMixin,  DetailView):
    model = ServicoExtraAssociadoModel
    template_name = 'app_servicos/single_servico_extra.html'
    context_object_name = 'servico'
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
        servico = self.get_object()
        extraassociado = servico.extra_associado

        entrada = servico.entrada_relacionada
        alteracoes_entrada = entrada.alteracoes.all() if entrada else []
        pagamentos = entrada.pagamentos.all().order_by("-data_pagamento") if entrada else []

        if entrada:
            valor_restante = entrada.valor_total - entrada.valor_pagamento
        else:
            valor_restante = None
            
        context.update({
            'entrada': entrada,
            'valor_restante': valor_restante,
            'historico_entrada': alteracoes_entrada,
            'pagamentos_entrada': pagamentos,
            'historico_servico': servico.historico_extra.all(),
            'extra_associado': servico.extra_associado
        })
        # Tipos relevantes: RG, RGP, NIT
        tipos_desejados = [
            'RG', 'RGP', 'NIT', 'CPF', 'CNH', 'CPF', 'TIE', 'CEI', 'CAEPF', 'Foto3x4', 
            'Comprovante Residência', 'Declaração Residência - MAPA',
            'Auto Declaração', 'Autorização de Acesso Gov Assinada',
            'Autorização de Uso de Imagem Assinada', 'Comprovante Seguro Defeso',
            'Ficha de Requerimento de Filiação Assinada', 'Título Eleitor',
            'Procuração Individual Ad Judicia Assinada', 'Procuração Individual Administrativa Assinada',
            'Licença Embarcação(Pesca)', 'Seguro DPEM','Protocolo RGP',
        ]
        tipos = TipoDocumentoModel.objects.filter(tipo__in=tipos_desejados)

        # Busca documentos do associado com esses tipos
        documentos_relevantes = Documento.objects.filter(
            extra_associado=extraassociado,
            tipo_doc__in=tipos
        ).order_by('-data_upload')

        context["documentos_relevantes"] = documentos_relevantes
        
        return context



# Lista de Serviços 
from django.db.models import Q, Value, CharField
from itertools import chain

class ListServicosView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    template_name = 'app_servicos/list_servicos.html'
    context_object_name = 'servicos'
    paginate_by = 50
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
        tipo_filtro = self.request.GET.get('tipo')
        termo_busca = self.request.GET.get('q', '').strip()

        # 🔍 SERVIÇOS DE ASSOCIADOS
        associados = ServicoAssociadoModel.objects.select_related(
            'associado__user', 'tipo_servico'
        ).annotate(origem=Value('associado', output_field=CharField()))

        # 🔍 SERVIÇOS DE EXTRA ASSOCIADOS
        extras = ServicoExtraAssociadoModel.objects.select_related(
            'extra_associado', 'tipo_servico'
        ).annotate(origem=Value('extra', output_field=CharField()))

        # 🔎 FILTRO POR NOME
        if termo_busca:
            associados = associados.filter(
                Q(associado__user__first_name__icontains=termo_busca) |
                Q(associado__user__last_name__icontains=termo_busca)
            )
            extras = extras.filter(
                Q(extra_associado__nome_completo__icontains=termo_busca)
            )

        # 🔂 Retorna conforme o tipo de filtro
        if tipo_filtro == 'associado':
            return associados.order_by('-data_inicio')
        elif tipo_filtro == 'extra':
            return extras.order_by('-data_inicio')

        # 🔀 Junta associados e extras
        merged = chain(associados, extras)

        # 🔠 Ordena por nome da pessoa (associado ou extra_associado)
        def obter_nome(servico):
            if hasattr(servico, 'associado') and servico.associado:
                return servico.associado.user.get_full_name().lower()
            elif hasattr(servico, 'extra_associado') and servico.extra_associado:
                return servico.extra_associado.nome_completo.lower()
            return ""

        return sorted(merged, key=obter_nome)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Todos os Serviços"
        context['filtro_ativo'] = self.request.GET.get('tipo', 'todos')
        context['termo_busca'] = self.request.GET.get('q', '')
        return context



# Create Serviço - ASSOCIADO
class CreateServicoAssociadoView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = ServicoAssociadoModel
    form_class = ServicoAssociadoForm
    template_name = 'app_servicos/create_servico_associado.html'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]

    def dispatch(self, request, *args, **kwargs):
        self.associado = get_object_or_404(AssociadoModel, id=kwargs.get('associado_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()

        associacao = self.associado.associacao  # 💡 define aqui antes de usar
        reparticao = self.associado.reparticao

        print("🔍 Initial associacao ID:", associacao.id if associacao else None)
        print("📦 Queryset associacoes:", list(AssociacaoModel.objects.all()))

        initial['associacao'] = associacao.id if associacao else None
        initial['reparticao'] = reparticao.id if reparticao else None

        return initial



    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['associacao'] = self.associado.associacao # ✅ Filtro da repartição
        return kwargs

    def form_valid(self, form):
        servico = form.save(commit=False)
        
        # 💡 VERIFIQUE se esse associado realmente existe aqui
        print("ASSOCIADO SETADO:", self.associado)

        servico.associado = self.associado
        servico.criado_por = self.request.user
        servico.save()
        return redirect('app_servicos:single_servico', pk=servico.pk)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['associado'] = self.associado
        context['nome_completo'] = self.associado.user.get_full_name()
        context['associacao'] =AssociacaoModel.objects.all()
        context['reparticoes'] = ReparticoesModel.objects.all()

        return context


# views.py
class EditServicoAssociadoView(LoginRequiredMixin,GroupPermissionRequiredMixin, UpdateView):
    model = ServicoAssociadoModel
    form_class = ServicoAssociadoForm
    template_name = 'app_servicos/edit_servico_associado.html'
    context_object_name = 'servico'
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
        return reverse('app_servicos:single_servico', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['editar_status'] = True  # 👈 Aqui habilita o campo
        return kwargs
    
    def form_valid(self, form):
        # 🔁 Pega o serviço original antes de salvar
        servico_original = self.get_object()

        # 🧠 Guarda os valores antes da edição
        dados_anteriores = {
            'content': servico_original.content,
            'status_etapa': servico_original.status_etapa,
        }

        form.instance.criado_por = self.request.user
        self.object = form.save(commit=False)

        # 🔍 Verifica alterações e registra
        campos_para_rastrear = ['content', 'status_etapa']
        for campo in campos_para_rastrear:
            valor_antigo = dados_anteriores.get(campo)
            valor_novo = getattr(self.object, campo)

            if str(valor_antigo) != str(valor_novo):
                ServicoHistoricoModel.objects.create(
                    servico_associado=self.object,
                    campo=campo.replace('_', ' ').capitalize(),
                    valor_antigo=valor_antigo,
                    valor_novo=valor_novo,
                    alterado_por=self.request.user
                )

        self.object.save()
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Serviço do Associado" 
        # Aqui acessa via self.object               
        servico = self.get_object()
        context['titulo'] = "Editar Serviço do Associado"        
        context['associado'] = servico.associado

        context['associacao'] =AssociacaoModel.objects.all()  # opcional
        return context


# ---------------Fim Serviço Associado------------------------------------------


# Criar Serviço - EXTRAASSOCIADO
class CreateServicoExtraAssociadoView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = ServicoExtraAssociadoModel
    form_class = ServicoExtraAssociadoForm
    template_name = 'app_servicos/create_servico_extra.html'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]

    def dispatch(self, request, *args, **kwargs):
        self.extra_associado = get_object_or_404(ExtraAssociadoModel, id=kwargs.get('extra_id'))
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # Se houver POST, tenta pegar associação da requisição
        if 'associacao' in self.request.POST:
            try:
                assoc_id = int(self.request.POST.get('associacao'))
                kwargs['associacao'] = AssociacaoModel.objects.get(pk=assoc_id)
            except (ValueError, AssociacaoModel.DoesNotExist):
                kwargs['associacao'] = None
        return kwargs
    

    def form_valid(self, form):
        servico = form.save(commit=False)
        servico.extra_associado = self.extra_associado
        servico.criado_por = self.request.user
        servico.save()

        # Monta a URL de criação de entrada com os dados via GET
        query_params = {
            'servico_extra_id': servico.id,
            'associacao': servico.associacao.id if servico.associacao else '',
            'reparticao': servico.reparticao.id if servico.reparticao else '',
            'tipo_servico': servico.tipo_servico.id if servico.tipo_servico else '',
            'content': servico.content,
        }

        url = reverse('app_finances:create_entrada') + '?' + urlencode(query_params)
        return redirect(url)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['extra_associado'] = self.extra_associado  # 💡 Esse é o nome que você usa no template
        context['servico_form'] = self.get_form()
        return context



# Editar Serviço Extra Associado
class EditServicoExtraAssociadoView(LoginRequiredMixin, GroupPermissionRequiredMixin, UpdateView):
    model = ServicoExtraAssociadoModel
    form_class = ServicoExtraAssociadoForm
    template_name = 'app_servicos/edit_servico_extra.html'
    context_object_name = 'servico'
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
        return reverse('app_servicos:single_servico_extra', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # 🔁 Recupera o objeto original antes do salvamento
        servico_original = self.get_object()

        # 👉 Guarda os valores antigos ANTES da alteração
        dados_anteriores = {
            'content': servico_original.content,
            'status_etapa': servico_original.status_etapa,
        }

        # ✅ Preserva a entrada vinculada
        form.instance.entrada_relacionada = servico_original.entrada_relacionada
        form.instance.criado_por = self.request.user

        # 👇 Salva temporariamente sem aplicar no banco ainda
        self.object = form.save(commit=False)

        # 🧠 Detecta alterações entre os dados antigos e novos
        campos_para_rastrear = ['content', 'status_etapa']
        for campo in campos_para_rastrear:
            valor_antigo = dados_anteriores.get(campo)
            valor_novo = getattr(self.object, campo)

            if str(valor_antigo) != str(valor_novo):
                ServicoHistoricoModel.objects.create(
                    servico_extra_associado=self.object,
                    campo=campo.replace('_', ' ').capitalize(),
                    valor_antigo=valor_antigo,
                    valor_novo=valor_novo,
                    alterado_por=self.request.user
                )

        self.object.save()  # ✅ Agora salva no banco com tudo certo
        return redirect(self.get_success_url())


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Serviço Extra"
        
        # Aqui acessa via self.object
        context['extra_associado'] = self.object.extra_associado
        context['nome_completo'] = self.object.extra_associado.nome_completo  # opcional
        return context


#------------------Fim Serviço Extra-Associado----------------------------------------------


# Carregamento de Repartições
def carregar_reparticoes(request):
    associacao_id = request.GET.get('associacao')
    reparticoes = ReparticoesModel.objects.filter(associacao_id=associacao_id).values('id', 'nome_reparticao')
    return JsonResponse(list(reparticoes), safe=False)

# Registros e histórico
def registrar_historico(servico, usuario):
    atual = model_to_dict(servico)
    original = model_to_dict(servico.__class__.objects.get(pk=servico.pk))

    campos_interessantes = [
        'content', 'tipo_servico', 'status_etapa', 'valor_servico', 'status_pagamento'
    ]

    for campo in campos_interessantes:
        if str(atual.get(campo)) != str(original.get(campo)):
            ServicoHistoricoModel.objects.create(
                servico=servico,
                campo=campo.replace('_', ' ').capitalize(),
                valor_antigo=original.get(campo),
                valor_novo=atual.get(campo),
                alterado_por=usuario
            )


# EXTRA-ASSOCIADOS
# Create Extra-associado
class CreateExtraAssociadoView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = ExtraAssociadoModel
    form_class = ExtraAssociadoForm
    template_name = 'app_servicos/create_extraassociado.html'
    context_object_name = 'extra_associado'
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
        messages.success(self.request, "Extra-associado cadastrado com sucesso!")
        return reverse_lazy('app_servicos:list_extraassociados')  # ou outra view

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Novo Extra-associado"
        return context

class EditExtraAssociadoView(LoginRequiredMixin, GroupPermissionRequiredMixin, UpdateView):
    model = ExtraAssociadoModel
    form_class = ExtraAssociadoForm
    template_name = 'app_servicos/edit_extraassociado.html'
    context_object_name = 'extra_associado'
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
        messages.success(self.request, "Extra-associado atualizado com sucesso!")
        return reverse_lazy('app_servicos:list_extraassociados')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Extra-associado"
        return context

# Lista de Extra-associados
class ListExtraAssociadosView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = ExtraAssociadoModel
    template_name = 'app_servicos/list_extraassociados.html'
    context_object_name = 'extra_associados'
    paginate_by = 50  # Ou qualquer valor ideal pra sua tela
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]
    
# Single Extra-associado
class DetailExtraAssociadoView(LoginRequiredMixin, GroupPermissionRequiredMixin, DetailView):
    model = ExtraAssociadoModel
    template_name = 'app_servicos/single_extra_associado.html'
    context_object_name = 'extra'
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

        extra = self.object

        # Documentos vinculados ao ExtraAssociado
        context['documentos'] = Documento.objects.filter(extra_associado=extra).order_by('-data_upload')

        # Serviços relacionados
        context['servicos'] = ServicoExtraAssociadoModel.objects.filter(extra_associado=extra)

        return context

# Painel Fluxo Etapas

from django.views.generic import TemplateView
from collections import defaultdict, OrderedDict
from .models import ServicoAssociadoModel, StatusEtapaChoices


from django.db.models import Value, CharField
from itertools import chain
from collections import OrderedDict

class PainelServicosEtapasView(LoginRequiredMixin, GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_servicos/painel_servicos_etapas.html'
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

        # Defina as etapas para documentos e outros serviços
        etapas_docs = [
            StatusEtapaChoices.PENDENTE,
            StatusEtapaChoices.DOC_PROTOCOLADO,
            StatusEtapaChoices.DOC_EXIGENCIA,                     
            StatusEtapaChoices.DOC_ANALISE,
            StatusEtapaChoices.DOC_RECURSO,
            StatusEtapaChoices.DOC_DEFERIDO,
            StatusEtapaChoices.DOC_INDEFERIDO,
        ]

        etapas_outros = [
            StatusEtapaChoices.PENDENTE,
            StatusEtapaChoices.SERVICO_ANDAMENTO,
            StatusEtapaChoices.SERVICO_ESPERA,
            StatusEtapaChoices.SERVICO_CONCLUIDO,
        ]

        # Serviços associados com natureza "emissao_documento"
        docs_assoc = ServicoAssociadoModel.objects.select_related(
            'associado__user', 'tipo_servico'
        ).filter(natureza_servico='emissao_documento').annotate(origem=Value('associado', output_field=CharField()))

        # Serviços associados com outras naturezas
        outros_assoc = ServicoAssociadoModel.objects.select_related(
            'associado__user', 'tipo_servico'
        ).filter(natureza_servico__in=['servico_consultoria', 'servico_geral']).annotate(origem=Value('associado', output_field=CharField()))

        # Serviços extra-associados com natureza "emissao_documento"
        docs_extra = ServicoExtraAssociadoModel.objects.select_related(
            'extra_associado', 'tipo_servico'
        ).filter(natureza_servico='emissao_documento').annotate(origem=Value('extra', output_field=CharField()))

        # Serviços extra-associados com outras naturezas
        outros_extra = ServicoExtraAssociadoModel.objects.select_related(
            'extra_associado', 'tipo_servico'
        ).filter(natureza_servico__in=['servico_consultoria', 'servico_geral']).annotate(origem=Value('extra', output_field=CharField()))

        # Junta associados + extras
        docs = sorted(chain(docs_assoc, docs_extra), key=lambda x: x.status_etapa)
        consultorias = sorted(chain(outros_assoc, outros_extra), key=lambda x: x.status_etapa)

        # Função para agrupar serviços por etapa
        def agrupar_por_etapa(queryset, etapas):
            grupos = OrderedDict()
            for etapa in etapas:
                grupos[etapa] = []

            for servico in queryset:
                if servico.status_etapa in grupos:
                    grupos[servico.status_etapa].append(servico)

            return grupos

        # Adiciona os painéis ao contexto
        context['painel_docs'] = agrupar_por_etapa(docs, etapas_docs)
        context['painel_consultorias'] = agrupar_por_etapa(consultorias, etapas_outros)
        context['status_labels'] = dict(StatusEtapaChoices.choices)

        return context
