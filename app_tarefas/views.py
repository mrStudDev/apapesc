from django.shortcuts import render, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import GroupPermissionRequiredMixin
from django.contrib.auth.models import Group
from .models import TarefaModel, HistoricoStatusModel, HistoricoResponsaveisModel
from .forms import TarefaForm
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import Http404
from app_associados.models import AssociadoModel
from app_associacao.models import IntegrantesModel, AssociacaoModel, ReparticoesModel
from app_documentos.models import Documento
from django.db.models import Count
from .models import GuiaINSSModel
from django.utils import timezone

class TarefaListView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = TarefaModel
    template_name = 'app_tarefas/list_tarefa.html'
    context_object_name = 'tarefas'
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
        user = self.request.user
        try:
            integrante = IntegrantesModel.objects.get(user=user)
            queryset = TarefaModel.objects.filter(arquivada=False).distinct().order_by('-data_criacao')
        except IntegrantesModel.DoesNotExist:
            queryset = TarefaModel.objects.filter(arquivada=False)

        # Aplica os filtros de status, categoria e prioridade
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria=categoria)

        prioridade = self.request.GET.get('prioridade')
        if prioridade:
            queryset = queryset.filter(prioridade=prioridade)

        # Aplica o filtro de busca se um termo for fornecido
        busca = self.request.GET.get('busca')
        if busca:
            queryset = queryset.filter(
                Q(titulo__icontains=busca) | Q(descricao__icontains=busca)
            )
            
        # Ordena primeiro por data_limite (priorizando as mais próximas),
        # e, se não tiver data_limite, ordena por data_criacao (mais recentes primeiro)
        queryset = queryset.order_by(
            F('data_limite').asc(nulls_last=True),  # Prioriza quem tem data_limite
            '-data_criacao'  # Em caso de empate, ordena por data de criação (mais recente primeiro)
        )            

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tarefas = self.get_queryset()

        # Contando tarefas por status
        context['total_pendentes'] = tarefas.filter(status='pendente').count()
        context['total_em_andamento'] = tarefas.filter(status='em_andamento').count()
        context['total_concluidas'] = tarefas.filter(status='concluida').count()
        context['total_devolvidas'] = tarefas.filter(status='devolvida').count()
        context['now'] = timezone.now().date() 
        context['total_tarefas'] = tarefas.count()
        context['busca'] = self.request.GET.get('busca', '')

        return context


class TarefaCreateView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = TarefaModel
    template_name = 'app_tarefas/create_tarefa.html'
    form_class = TarefaForm
    success_url = reverse_lazy('app_tarefas:list_tarefas')
    context_object_name = 'tarefas'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]
    
    def get_initial(self):
        # Preenche o campo associado se o parâmetro estiver na URL
        associado_id = self.kwargs.get('associado_id')
        initial_data = super().get_initial()
        if associado_id:
            initial_data['associado'] = AssociadoModel.objects.filter(id=associado_id).first()
        return initial_data

    def form_valid(self, form):
        # Salva a tarefa e atribui o criador
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        # Redireciona para a página do associado caso tenha sido criado a partir dele
        associado_id = self.kwargs.get('associado_id')
        if associado_id:
            return reverse('app_associados:single_associado', kwargs={'pk': associado_id})
        return super().get_success_url()


class TarefaEditView(LoginRequiredMixin, GroupPermissionRequiredMixin, UpdateView):
    model = TarefaModel
    template_name = 'app_tarefas/edit_tarefa.html'
    form_class = TarefaForm    
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
        # Preenche o campo 'criado_por' com o usuário logado sempre
        form.instance.criado_por = self.request.user
        # Inicializa o objeto, mas não salva ainda - ==========
        self.object = form.save(commit=False)
        # Obter o estado atual da tarefa antes de salvar as mudanças
        tarefa_antiga = TarefaModel.objects.get(pk=self.object.pk)

        # Comparar e registrar mudanças de status
        if form.instance.status != tarefa_antiga.status:
            HistoricoStatusModel.objects.create(
                tarefa=self.object,
                status_anterior=tarefa_antiga.status,
                status_novo=form.instance.status,
                alterado_por=self.request.user.integrante
            )

        # Comparar e registrar mudanças de responsáveis
        responsaveis_anteriores = set(tarefa_antiga.responsaveis.all())
        novos_responsaveis = set(form.cleaned_data['responsaveis'])

        if responsaveis_anteriores != novos_responsaveis:
            historico_responsaveis = HistoricoResponsaveisModel.objects.create(
                tarefa=self.object,
                alterado_por=self.request.user.integrante
            )
            historico_responsaveis.responsaveis_anteriores.set(responsaveis_anteriores)
            historico_responsaveis.responsaveis_novos.set(novos_responsaveis)
            historico_responsaveis.save()
            
        # Agora salva o objeto atualizado
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Lista de status disponíveis para alteração
        context['status_choices'] = self.model._meta.get_field('status').choices
        # Lista de responsáveis disponíveis
        context['responsaveis_disponiveis'] = IntegrantesModel.objects.all()

        # Responsáveis atribuídos atualmente à tarefa
        context['responsavel_atual'] = self.object.responsaveis.all()

        context['associado'] = self.object.associado

        return context

    def get_success_url(self):
        # Redireciona para a página de detalhes da tarefa com o pk da instância 
        return reverse_lazy('app_tarefas:single_tarefa', kwargs={'pk': self.object.pk})
    

class TarefaDetailView(LoginRequiredMixin, GroupPermissionRequiredMixin, DetailView):
    model = TarefaModel
    template_name = 'app_tarefas/single_tarefa.html'
    context_object_name = 'tarefa'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]
    
    def get_object(self, queryset=None):
        """
        Sobrescreve o método get_object para garantir que todos os integrantes possam acessar a tarefa.
        """
        tarefa = get_object_or_404(TarefaModel, pk=self.kwargs['pk'])
        return tarefa


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Lista de status disponíveis para alteraçãos
        context['status_choices'] = self.model._meta.get_field('status').choices
        # Lista de responsáveis disponíveis
        context['responsaveis_disponiveis'] = IntegrantesModel.objects.all()

        # Responsáveis atribuídos atualmente à tarefa
        context['responsavel_atual'] = self.object.responsaveis.all()

        context['associado'] = self.object.associado
        context['documentos'] = Documento.objects.filter(tarefa=self.object)
        
        return context


def alterar_status_tarefa(request, pk):
    if request.method == "POST":
        tarefa = get_object_or_404(TarefaModel, pk=pk)
        novo_status = request.POST.get('status')

        if not novo_status or novo_status == tarefa.status:
            return JsonResponse({'success': False, 'message': 'Status inválido ou inalterado.'})

        # Registra o histórico de alterações
        HistoricoStatusModel.objects.create(
            tarefa=tarefa,
            status_anterior=tarefa.status,
            status_novo=novo_status,
            alterado_por=request.user.integrante  # Assumindo que o usuário está vinculado a um IntegrantesModel
        )

        # Atualiza o status da tarefas
        tarefa.status = novo_status
        tarefa.save()

        return JsonResponse({'success': True, 'message': 'Status alterado com sucesso!'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'}, status=405)



def alterar_responsaveis_tarefa(request, pk):
    if request.method == "POST":
        tarefa = get_object_or_404(TarefaModel, pk=pk)
        novos_responsaveis_ids = request.POST.getlist('responsaveis')

        # Identificar responsáveis antigos e novos
        responsaveis_atuais = set(tarefa.responsaveis.values_list('id', flat=True))
        novos_responsaveis = set(map(int, novos_responsaveis_ids))

        # Determinar acréscimos e remoções
        adicionados = novos_responsaveis - responsaveis_atuais
        removidos = responsaveis_atuais - novos_responsaveis

        if not adicionados and not removidos:
            return JsonResponse({'success': False, 'message': 'Nenhuma alteração feita.'})

        # Criar o histórico
        historico = HistoricoResponsaveisModel.objects.create(
            tarefa=tarefa,
            alterado_por=request.user.integrante  # Assumindo que o usuário está vinculado a um IntegrantesModel
        )
        historico.responsaveis_anteriores.set(tarefa.responsaveis.all())
        historico.responsaveis_novos.set(IntegrantesModel.objects.filter(id__in=novos_responsaveis))
        historico.save()

        # Atualizar os responsáveis na tarefa
        tarefa.responsaveis.set(IntegrantesModel.objects.filter(id__in=novos_responsaveis))
        tarefa.save()

        return JsonResponse({
            'success': True,
            'message': 'Responsáveis alterados com sucesso!',
            'adicionados': list(adicionados),
            'removidos': list(removidos),
        })

    return JsonResponse({'success': False, 'message': 'Método não permitido.'}, status=405)



class TarefaBoardView(LoginRequiredMixin, GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_tarefas/board_tarefas.html'
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
        """ 🔥 Retorna TODAS as tarefas para TODOS os integrantes """
        return TarefaModel.objects.all().distinct().order_by('-data_criacao')
        
        
    def get_context_data(self, **kwargs):
        """
        Organiza as tarefas em colunas por status e limita a visualização.
        """
        context = super().get_context_data(**kwargs)
        
        # Resgata as tarefas organizadas por status
        tarefas = self.get_queryset()
        context['tarefas_por_status'] = {
        status_label: tarefas.filter(status=status_key)
        for status_key, status_label in TarefaModel.STATUS_TAREFA
    }
        tarefas = self.get_queryset()
        context['pendentes'] = tarefas.filter(status='pendente')
        context['em_andamento'] = tarefas.filter(status='em_andamento')
        context['concluidas'] = tarefas.filter(status='concluida')
        context['devolvidas'] = tarefas.filter(status='devolvida')
        
        # Adiciona contagens ao contexto
        context['contagem_tarefas'] = {
            'pendentes': context['pendentes'].count(),
            'em_andamento': context['em_andamento'].count(),
            'concluidas': context['concluidas'].count(),
            'devolvidas': context['devolvidas'].count(),
        }
                
        return context


def alterar_status_tarefa_board(request, pk):
    if request.method == "POST":
        data = json.loads(request.body)
        tarefa = get_object_or_404(TarefaModel, pk=pk)
        novo_status = data.get('status')
        
        if not novo_status:
            return JsonResponse({'success': False, 'message': 'Status não informado.'}, status=400)

        if novo_status != tarefa.status:
            # Registrar histórico
            HistoricoStatusModel.objects.create(
                tarefa=tarefa,
                status_anterior=tarefa.status,
                status_novo=novo_status,
                alterado_por=getattr(request.user, 'integrante', None)
            )
            # Atualizar status
            tarefa.status = novo_status
            tarefa.save()

        return JsonResponse({'success': True, 'message': 'Status atualizado com sucesso!'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'}, status=405)


class TarefaArquivadaListView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = TarefaModel
    template_name = 'app_tarefas/tarefas_arquivadas.html'
    context_object_name = 'tarefas'
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
        user = self.request.user
        try:
            integrante = IntegrantesModel.objects.get(user=user)
            return TarefaModel.objects.filter(
                Q(arquivada=True)
            ).distinct()
        except IntegrantesModel.DoesNotExist:
            return TarefaModel.objects.filter(arquivada=True)


@login_required
def arquivar_tarefa(request, pk):
    if request.method == "POST":
        tarefa = get_object_or_404(TarefaModel, pk=pk)
        if not tarefa.arquivada:
            tarefa.arquivada = True
            tarefa.status = 'arquivada'  # Define o status como arquivada, caso necessário
            tarefa.save()
            messages.success(request, 'Tarefa arquivada com sucesso!')
        else:
            messages.warning(request, 'A tarefa já estava arquivada.')

        # Redirecionar para a lista de tarefas arquivadas
        return redirect('app_tarefas:tarefas_arquivadas')

    messages.error(request, 'Método não permitido.')
    return redirect('app_tarefas:list_tarefas')


@login_required
def desarquivar_tarefa(request, pk):
    if request.method == "POST":
        tarefa = get_object_or_404(TarefaModel, pk=pk)
        if tarefa.arquivada:
            tarefa.arquivada = False
            tarefa.status = 'pendente'  # Define o status como pendente ao desarquivar
            tarefa.save()
            messages.success(request, 'Tarefa desarquivada com sucesso!')
        else:
            messages.warning(request, 'A tarefa não estava arquivada.')

        # Redirecionar para a lista de tarefas ativas
        return redirect('app_tarefas:list_tarefas')

    messages.error(request, 'Método não permitido.')
    return redirect('app_tarefas:tarefas_arquivadas')


class TarefaDeleteView(LoginRequiredMixin, GroupPermissionRequiredMixin, DeleteView):
    model = TarefaModel
    template_name = 'app_tarefas/delete_tarefa.html'
    success_url = reverse_lazy('app_tarefas:list_tarefas')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]




# ========= INSS =========

class EmissaoGuiasView(LoginRequiredMixin, TemplateView):
    template_name = "app_tarefas/emissao_guias.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ano_selecionado = self.request.GET.get("ano", now().year)
        meses_validos = list(range(4, 12))  # Abril a Novembro

        # 🔥 Filtra somente associados que recolhem INSS e inclui CPF e Senha_Gov
        associados_inss = AssociadoModel.objects.filter(recolhe_inss="Sim").values(
            "id", "user__first_name", "user__last_name", "cpf", "senha_gov", "celular_correspondencia"
        )


        guias_por_associado = {}
        for associado in associados_inss:
            associado_id = associado["id"]  # ✅ Garante que ID está presente
            guias = {mes: None for mes in meses_validos}
            guias_existentes = GuiaINSSModel.objects.filter(associado_id=associado_id, ano=ano_selecionado)

            for guia in guias_existentes:
                guias[guia.mes_referencia] = guia  # ✅ Associamos corretamente

            guias_por_associado[associado_id] = {
                "dados": associado,
                "guias": guias
            }


        context.update({
            "ano_selecionado": int(ano_selecionado),
            "anos_disponiveis": range(2022, now().year + 1),  # Mostra anos de 2023 até o atual
            "meses_validos": meses_validos,
            "associados_inss": associados_inss,
            "guias_por_associado": guias_por_associado,
        })
        return context



@method_decorator(login_required, name='dispatch')
class CriarGuiaView(View):
    def post(self, request, associado_id, mes, ano):
        associado = get_object_or_404(AssociadoModel, id=associado_id)

        # Verifica se a guia já existe
        guia, created = GuiaINSSModel.objects.get_or_create(
            associado=associado,
            mes_referencia=mes,
            ano=ano,
            defaults={"status": "pendente"},
        )

        if created:
            messages.success(request, f"Guia de {mes}/{ano} criada para {associado.user.get_full_name()}.")

        return JsonResponse({"success": True, "guia_id": guia.id})


class AtualizarStatusGuiaView(LoginRequiredMixin, View):
    def post(self, request, guia_id):
        guia = get_object_or_404(GuiaINSSModel, id=guia_id)
        
        if guia.status == "pendente":
            guia.status = "emitido"
            messages.success(request, f"Guia {guia.get_mes_referencia_display()} marcada como EMITIDA.")
        elif guia.status == "emitido":
            guia.status = "enviado"
            messages.success(request, f"Guia {guia.get_mes_referencia_display()} marcada como ENVIADA.")
        
        guia.save()
        return redirect("app_tarefas:emissao_guias")

