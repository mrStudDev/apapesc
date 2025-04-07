from django.shortcuts import render, get_object_or_404, redirect
from .models import ControleBeneficioModel, BeneficioModel, ControleBeneficioHistoricoModel
from django.db.models import Q
from django.db import transaction
from .forms import ControleBeneficioForm, BeneficioModelForm
from .models import UF_CHOICES  # Import UF_CHOICES from the models
from django.contrib import messages
from django.views.generic import CreateView, ListView
from .utils import upload_to_drive
import os
from django.views.generic import TemplateView
from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from collections import OrderedDict
from datetime import date
from collections import OrderedDict
from app_associados.models import AssociadoModel
from django.db import transaction
from django.contrib.auth.decorators import login_required, permission_required



# Lista de Controle de Benefícios
def lista_beneficios(request):
    controles = ControleBeneficioModel.objects.select_related('beneficio', 'associado__user')

    beneficio_filtro = request.GET.get('beneficio')
    status = request.GET.get('status')
    nome_associado = request.GET.get('nome_associado')  # Novo parâmetro

    if beneficio_filtro:
        partes = beneficio_filtro.split('__')
        nome = partes[0]
        ano = partes[1] if len(partes) > 1 else None
        estado = partes[2] if len(partes) > 2 else None
        
        controles = controles.filter(beneficio__nome=nome)
        
        if ano:
            controles = controles.filter(beneficio__ano_concessao=ano)
        if estado:
            controles = controles.filter(beneficio__estado=estado)

    if status:
        controles = controles.filter(status_pedido=status)

    if nome_associado:
        controles = controles.filter(
            Q(associado__user__first_name__icontains=nome_associado) |
            Q(associado__user__last_name__icontains=nome_associado)
        )

    controles = controles.order_by('associado__user__first_name', 'associado__user__last_name')

    # Agrupar benefícios disponíveis por nome para o template
    beneficios_agrupados = {}
    for beneficio in BeneficioModel.objects.order_by('-ano_concessao', 'nome'):
        if beneficio.nome not in beneficios_agrupados:
            beneficios_agrupados[beneficio.nome] = []
        beneficios_agrupados[beneficio.nome].append(beneficio)

    return render(request, 'app_beneficios/list_beneficios.html', {
        'controles': controles,
        'beneficios_agrupados': beneficios_agrupados,
        'status_choices': ControleBeneficioModel._meta.get_field('status_pedido').choices,
        'uf_choices': UF_CHOICES,
        'nome_associado': nome_associado or ''  # Passa o valor atual para o template
    })


def controle_beneficio_detail(request, pk):
    controle = get_object_or_404(ControleBeneficioModel, pk=pk)
    
    if request.method == 'POST':
        form = ControleBeneficioForm(request.POST, request.FILES, instance=controle)
        if form.is_valid():
            # Associa o usuário atual antes de salvar
            controle._current_user = request.user
            controle.save()
            messages.success(request, 'Registro atualizado com sucesso!')
            return redirect('app_beneficios:lista_beneficios')
    else:
        form = ControleBeneficioForm(instance=controle)
    
    return render(request, 'app_beneficios/controle_detail.html', {
        'form': form,
        'controle': controle,
        'historico': controle.historico.all().order_by('-alterado_em')
    })


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


# app_beneficios/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import date
from app_associados.models import AssociadoModel
from .models import BeneficioModel, ControleBeneficioModel

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


class PainelBeneficiosView(LoginRequiredMixin, TemplateView):
    template_name = 'app_beneficios/painel_beneficios.html'

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


class AdicionarBeneficioView(CreateView):
    model = BeneficioModel
    form_class = BeneficioModelForm
    template_name = 'app_beneficios/create_beneficio.html'
    success_url = reverse_lazy('app_beneficios:lista_beneficios')

    def form_valid(self, form):
        messages.success(self.request, "✅ Benefício cadastrado com sucesso!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "⚠️ Erro ao cadastrar. Verifique os campos.")
        return super().form_invalid(form)


def lista_e_edita_beneficios(request):
    beneficios = BeneficioModel.objects.order_by('-ano_concessao', 'nome')
    beneficio_editando = None  # Inicializa a variável no topo

    if request.method == 'POST':
        beneficio_id = request.POST.get('beneficio_id')
        beneficio = get_object_or_404(BeneficioModel, pk=beneficio_id)
        form = BeneficioModelForm(request.POST, instance=beneficio, modo_edicao=True)
        beneficio_editando = beneficio

        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Benefício '{beneficio.get_nome_display()}' atualizado com sucesso!")
            return redirect('app_beneficios:beneficios')
        else:
            messages.error(request, "⚠️ Erro ao salvar os dados. Verifique os campos.")

    else:
        beneficio_id = request.GET.get('id')
        if beneficio_id:
            beneficio_editando = get_object_or_404(BeneficioModel, pk=beneficio_id)
            form = BeneficioModelForm(instance=beneficio_editando, modo_edicao=True)
        else:
            form = BeneficioModelForm()  # Form vazio para criação

    return render(request, 'app_beneficios/edit_beneficio.html', {
        'beneficios': beneficios,
        'form': form,
        'beneficio_editando': beneficio_editando,
    })


# Benefícios 
class BeneficioListView(ListView):
    model = BeneficioModel
    template_name = 'app_beneficios/beneficios.html'
    context_object_name = 'beneficios'
    ordering = ['-ano_concessao', 'nome', 'estado']
    


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
    