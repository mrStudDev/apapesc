from django.shortcuts import render, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib import messages
from django.utils.timezone import now, timezone
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import GroupPermissionRequiredMixin
from django.contrib.auth.models import Group
from .forms import TarefaForm, LancamentoINSSForm, TarefaMassaForm
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import transaction
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
from .models import LancamentoINSSModel, GuiaINSSModel
from django.template.loader import render_to_string
from django.utils import timezone
from decimal import Decimal
from django.views.decorators.http import require_POST
from django.db import IntegrityError
import calendar
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from .models import GuiaINSSModel, LancamentoINSSModel
from django.contrib.auth import get_user_model
from app_tarefas.utils import buscar_tarefas_do_lancamento, criar_lancamento_reaps


from .models import (
    TarefaModel,
    HistoricoStatusModel,
    HistoricoResponsaveisModel,
    ProgressoGuiaINSSModel,
    RodadaProcessamentoINSS,
    GuiaRodadaProcessada,
    TarefaMassaModel,
    ChecklistITarefastemModel,
    ProcessamentoTarefaMassa,
    RodadaProcessamentoTarefaMassa,
    ReapsAnualModel,
    ReapsAssociadoItem,
    
)

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


    def get(self, request, *args, **kwargs):
        rodada_id = request.GET.get("rodada_id")
        if rodada_id:
            tarefa = self.get_object()
            try:
                with transaction.atomic():
                    rodada = RodadaProcessamentoTarefaMassa.objects.get(pk=rodada_id)
                    proc = ProcessamentoTarefaMassa.objects.select_for_update().get(
                        tarefa=tarefa,
                        rodada=rodada
                    )
                        
                    if proc.status == 'em_processamento' and proc.processado_por != request.user:
                        messages.warning(request, "Essa tarefa já está sendo processada por outro usuário.")
                        return redirect('app_tarefas:gerar_tarefa_massa')

                    if proc.status == 'nao_processada' and proc.processado_por is None:
                        proc.status = 'em_processamento'
                        proc.processado_por = request.user
                        proc.iniciado_em = timezone.now()  # ✅ Manter!
                        proc.save()

            except ProcessamentoTarefaMassa.DoesNotExist:
                messages.error(request, "Erro ao localizar processamento dessa tarefa.")
                return redirect('app_tarefas:gerar_tarefa_massa')

        return super().get(request, *args, **kwargs)


    def post(self, request, pk):
        tarefa = get_object_or_404(TarefaModel, pk=pk)  # <- TEM que vir aqui antes de tudo!

        # ✅ PAUSAR a tarefa e voltar
        if request.POST.get("acao") == "pausar":
            rodada_id = request.POST.get("rodada_id")
            if rodada_id:
                try:
                    rodada = RodadaProcessamentoTarefaMassa.objects.get(pk=rodada_id)
                    proc = ProcessamentoTarefaMassa.objects.get(tarefa=tarefa, rodada=rodada)

                    if proc.status == 'em_processamento' and proc.processado_por == request.user:
                        proc.status = 'nao_processada'
                        proc.processado_por = None
                        proc.iniciado_em = None
                        proc.save()
                        messages.info(request, "Tarefa pausada com sucesso.")
                except Exception as e:
                    messages.warning(request, f"Erro ao tentar pausar a tarefa: {str(e)}")

            return redirect('app_tarefas:gerar_tarefa_massa')

        # Atualizar responsáveis
        if 'responsaveis' in request.POST:
            novos_responsaveis = request.POST.getlist('responsaveis')
            tarefa.responsaveis.set(novos_responsaveis)
            messages.success(request, "Responsáveis atualizados com sucesso!")

        # Atualizar checklist
        for item in tarefa.checklist_itens.all():
            checkbox_name = f"item_{item.id}"
            item.concluido = checkbox_name in request.POST
            item.save()

        for item in ChecklistITarefastemModel.objects.filter(tarefa=tarefa):
            checkbox_name = f"item_mass_{item.id}"
            item.concluido = checkbox_name in request.POST
            item.save()

        # ✅ Processamento da rodada
        rodada_id = request.POST.get("rodada_id")
        if rodada_id and rodada_id.isdigit():
            try:
                rodada = RodadaProcessamentoTarefaMassa.objects.get(pk=rodada_id)
                proc = ProcessamentoTarefaMassa.objects.get(tarefa=tarefa, rodada=rodada)

                if proc.status == 'em_processamento' and proc.processado_por != request.user:
                    messages.error(request, "Esta tarefa já está sendo processada por outro usuário.")
                    return redirect('app_tarefas:gerar_tarefa_massa')

                proc.status = 'processada'
                proc.save()

                # 🔍 Busca próxima tarefa disponível
                proxima_proc = rodada.tarefas_processadas.filter(
                    status='nao_processada',
                    tarefa__status__in=['pendente', 'em_andamento']
                ).exclude(
                    Q(status='em_processamento') & ~Q(processado_por=request.user)
                ).order_by('atualizado_em').first()

                if proxima_proc:
                    return redirect(
                        f"{reverse('app_tarefas:single_tarefa', kwargs={'pk': proxima_proc.tarefa.pk})}?rodada_id={rodada.pk}"
                    )
                else:
                    # ✅ Encerrando a rodada corretamente
                    rodada.encerrada = True
                    rodada.save()
                    messages.success(request, "Todas as tarefas da rodada foram processadas. Rodada encerrada.")
                    return redirect('app_tarefas:list_tarefas')

            except (RodadaProcessamentoTarefaMassa.DoesNotExist, ProcessamentoTarefaMassa.DoesNotExist):
                messages.error(request, "Erro ao atualizar o processamento da tarefa.")
                return redirect('app_tarefas:gerar_tarefa_massa')
        return redirect('app_tarefas:single_tarefa', pk=tarefa.pk)

        
    def get_object(self, queryset=None):
        """
        Sobrescreve o método get_object para garantir que todos os integrantes possam acessar a tarefa.
        """
        tarefa = get_object_or_404(TarefaModel, pk=self.kwargs['pk'])
        return tarefa


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tarefa = self.get_object()

        rodada_id = self.request.GET.get("rodada_id") or self.request.POST.get("rodada_id")
        context["rodada_id"] = rodada_id

        context['status_choices'] = self.model._meta.get_field('status').choices
        context['responsaveis_disponiveis'] = IntegrantesModel.objects.all()
        context['responsavel_atual'] = self.object.responsaveis.all()
        context['associado'] = self.object.associado
        context['documentos'] = Documento.objects.filter(tarefa=self.object)

        # Checklist padrão
        checklist = self.object.checklist_itens.all()
        total = checklist.count()
        feitos = checklist.filter(concluido=True).count()
        progresso_percentual = int((feitos / total) * 100) if total > 0 else 0

        # Checklist de massa
        checklist_massas = ChecklistITarefastemModel.objects.filter(tarefa=tarefa)
        total_massas = checklist_massas.count()
        feitos_massas = checklist_massas.filter(concluido=True).count()
        progresso_massas = int((feitos_massas / total_massas) * 100) if total_massas > 0 else 0

        # Rodada de processamento (se houver)
        if rodada_id:
            try:
                rodada = RodadaProcessamentoTarefaMassa.objects.get(pk=rodada_id)

                # Contagens
                contagem = rodada.tarefas_processadas.aggregate(
                    total=Count('id'),
                    processadas=Count('id', filter=Q(status='processada')),
                    em_processamento=Count('id', filter=Q(status='em_processamento')),
                    nao_processadas=Count('id', filter=Q(status='nao_processada')),
                )

                # 👇 Adiciona manualmente o campo de concluídas
                contagem["concluidas"] = TarefaModel.objects.filter(
                    massa=rodada.tarefa_massa,
                    status='concluida'
                ).count()

                # Usuários participando
                usuarios_atuais = rodada.tarefas_processadas.filter(
                    status='em_processamento',
                    processado_por__isnull=False
                ).select_related('processado_por').values_list(
                    'processado_por__first_name', flat=True
                ).distinct()

                context.update({
                    'rodada_em_andamento': True,
                    'rodada_obj': rodada,
                    'usuarios_em_processamento': usuarios_atuais,
                    'contagem_tarefas_rodada': contagem,
                })

            except RodadaProcessamentoTarefaMassa.DoesNotExist:
                context['rodada_em_andamento'] = False

        context.update({
            'checklist_itens': checklist,
            'total_itens': total,
            'feitos_itens': feitos,
            'progresso': progresso_percentual,
            'checklist_massas': checklist_massas,
            'total_massas': total_massas,
            'feitos_massas': feitos_massas,
            'progresso_massas': progresso_massas,
        })

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

        # ✅ Recupera o integrante logado
        try:
            integrante = request.user.integrante
        except IntegrantesModel.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Usuário não está vinculado a um integrante.'}, status=400)

        # Criar o histórico
        historico = HistoricoResponsaveisModel.objects.create(
            tarefa=tarefa,
            alterado_por=integrante
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

# ==============================fim    
# Minhas Tarefas


class MinhasTarefasView(LoginRequiredMixin, TemplateView):
    template_name = "app_tarefas/minhas_tarefas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        try:
            integrante = IntegrantesModel.objects.get(user=user)
        except IntegrantesModel.DoesNotExist:
            integrante = None

        # 👤 Tarefas criadas por mim
        tarefas_criadas_por_mim = TarefaModel.objects.filter(criado_por=user).order_by('-data_criacao')

        # 🧾 Tarefas atribuídas a mim (por outro usuário)
        tarefas_atribuídas = TarefaModel.objects.none()
        if integrante:
            tarefas_atribuídas = TarefaModel.objects.filter(responsaveis=integrante).exclude(criado_por=user).order_by('-data_criacao')

        context["tarefas_criadas"] = tarefas_criadas_por_mim
        context["tarefas_atribuidas"] = tarefas_atribuídas

        return context


    
# ==============================fim    
# Tarefas em Massa
class GerarTarefaMassaView(View):
    template_name = 'app_tarefas/gerar_tarefa_massa.html'
    confirm_template = 'app_tarefas/confirmar_tarefa_massa.html'
    
    def get(self, request):
        form = TarefaMassaForm()
        historico = self._get_historico_completo()
        return render(request, self.template_name, {
            'form': form,
            'historico': historico
        })

    def post(self, request):
        if 'confirmado' in request.POST:
            # Segundo POST — gerar tarefas de fato
            tipo = request.POST.get('tipo')
            associados = AssociadoModel.objects.filter(
                status__in=["Associado Lista Ativo(a)", "Associado Lista Aposentado(a)"]
            )
            tarefas_criadas = []

            lancamento = TarefaMassaModel.objects.create(
                tipo=tipo,
                criado_por=request.user,
            )

            for associado in associados:
                titulo, descricao, content = self._gerar_conteudo(tipo, associado)

                tarefa = TarefaModel.objects.create(
                    criado_por=request.user,
                    titulo=titulo,
                    descricao=descricao,
                    categoria='associado',
                    prioridade='media',
                    status='pendente',
                    associado=associado,
                    data_limite=now().date() + timedelta(days=30),
                    content=content,
                    massa=lancamento
                )

                if tipo == 'recadastramento_dados':
                    self._criar_checklist_recadastramento(tarefa)

                tarefas_criadas.append(tarefa)

            lancamento.total_geradas = len(tarefas_criadas)
            lancamento.save()

            messages.success(request, f"{len(tarefas_criadas)} tarefas criadas com sucesso.")
            return redirect('app_tarefas:gerar_tarefa_massa')

        else:
            form = TarefaMassaForm(request.POST)
            if form.is_valid():
                tipo = form.cleaned_data['tipo']
                associados = AssociadoModel.objects.filter(
                    status__in=["Associado Lista Ativo(a)", "Associado Lista Aposentado(a)"]
                )
                return render(request, self.confirm_template, {
                    'tipo': tipo,
                    'total': associados.count()
                })

            historico = self._get_historico_completo()
            return render(request, self.template_name, {
                'form': form,
                'historico': historico
            })

    def _get_historico_completo(self):
        historico = TarefaMassaModel.objects.select_related('criado_por').prefetch_related('rodadas').order_by('-criado_em')[:20]

        for massa in historico:
            ultima_rodada = massa.rodadas.last()
            massa.ultima_rodada = ultima_rodada

            if ultima_rodada:
                massa.tem_tarefa_nao_concluida = ultima_rodada.tarefas_processadas.filter(
                    ~Q(status='processada'),
                    ~Q(tarefa__status='concluida')
                ).exists()
            else:
                massa.tem_tarefa_nao_concluida = False

            # 🧮 Conta tarefas concluídas e pendentes
            massa.total_concluidas = massa.tarefas_geradas.filter(status='concluida').count()
            massa.total_pendentes = massa.tarefas_geradas.exclude(status='concluida').count()

        return historico


    def _gerar_conteudo(self, tipo, associado):
        nome = associado.user.get_full_name() if associado.user else f"Associado #{associado.id}"
        ano = now().year

        if tipo == 'recadastramento_dados':
            return (
                f"Recadastramento de Dados - {nome}",
                f"Tarefa de recadastramento de dados ({ano})",
                f"""Tarefa de Recadastramento do associado {nome}.

Lembre-se de:
- Checar a validade dos documentos;
- Validar e atualizar o e-mail do associado;
- Confirmar se todos os dados cadastrais estão atualizados.
"""
            )

        elif tipo == 'abertura_contas':
            return (
                f"Abertura de Conta para {nome}",
                f"Abertura de conta bancária ({ano})",
                f"""Tarefa de abertura de conta para o associado {nome}.

Atenção:
- Crie uma senha forte e segura;
- Não compartilhe dados com terceiros;
- Confirme os dados bancários fornecidos.
"""
            )

        elif tipo == 'inscricoes_cursos':
            return (
                f"Incrição de {nome} em curso",
                f"Incrição em cursos internos ({ano})",
                f"""Tarefa de inscrição em cursos para o associado {nome}.

Instruções:
- Validar interesse do associado;
- Confirmar disponibilidade de vagas;
- Atualizar o sistema com o status da inscrição.
"""
            )

        return (
            f"Tarefa Geral - {nome}",
            f"Tarefa geral para o associado - {ano}",
            f"""Conteúdo padrão para tarefa genérica atribuída a {nome}."""
        )

    def _criar_checklist_recadastramento(self, tarefa):
        itens = [
        "📄 RECADASTRAMENTO - Ficha de Requerimento de Filiação assinada? Já possui???",
        "📄 Procuração Individual assinadaxx",
        "⚠️ Assinar também a Procuração Geral para o Defeso",
        "🖼️ Declaração de Uso de Direitos de Imagem",
        "🗒️ Declaração de Autorização de Acesso ao GOV",
        "🪪 RG (legível e atualizado)",
        "🪪 CPF",
        "🚗 CNH (se possuir)",
        "🧾 NIT (emitir pelo INSS, se não tiver)",
        "🧾 CEI",
        "🧾 CAEPF (emitir pelo E-social, se não tiver)",
        "🗳️ Título de Eleitor",
        "🏠 Comprovante de Residência atualizado",
        "📝 Declaração de Residência (Modelo MAPA) — obrigatório para RGP",
        "🖼️ Foto 3x4 recente",
        "🎣 RGP (Registro Geral da Pesca) — solicitar ao MAPA se não possuir",
        "📄 TIE — Título de Inscrição da Embarcação",
        "📄 Licença de Pesca válida",
        "📑 Seguro DPEM vigente",
        "🛠️ Verificar cadastro e documentação da embarcação",
        "💬 Adicionar no grupo de WhatsApp da associação",
        "📝 Verificar e atualizar os campos 'Recolhe INSS' e 'Recebe Seguro'",
        "🧾 Verificar se já recebeu benefício do Governo (Bolsa Família, seguro defeso, etc.)",
        "📜 Enviar orientações gerais sobre direitos e deveres do associado",
        "💰 Orientar sobre o pagamento das anuidades",
        "🔍 Confirmar dados cadastrais completos no sistema",
        "📅 Agendar reunião ou orientação inicial, se necessário",
        "📂 Garantir que todos os uploads estão feitos e legíveis",
        "✍️ Verificar assinatura presencial, se houver pendência",
    ]


        for item in itens:
            ChecklistITarefastemModel.objects.create(
                tarefa=tarefa,
                descricao=item
            )
            

# Processamenro em rodadas de Tarefas em MAssa
# views.py
class IniciarRodadaProcessamentoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        tarefa_massa = get_object_or_404(TarefaMassaModel, pk=pk)

        # 🔒 Impede múltiplas rodadas simultâneas
        if RodadaProcessamentoTarefaMassa.objects.filter(tarefa_massa=tarefa_massa, encerrada=False).exists():
            messages.warning(request, "Já existe uma rodada ativa para esse lançamento.")
            return redirect('app_tarefas:gerar_tarefa_massa')

        # 🧹 Limpa rodadas anteriores
        RodadaProcessamentoTarefaMassa.objects.filter(tarefa_massa=tarefa_massa).delete()

        # 🎯 Busca tarefas válidas (filtrando concluídas!)
        tarefas = tarefa_massa.tarefas_geradas.exclude(status='concluida')

        # 🚀 Cria nova rodada
        rodada = RodadaProcessamentoTarefaMassa.objects.create(
            tarefa_massa=tarefa_massa,
            criada_por=request.user
        )

        # 📋 Cria registros de processamento
        for tarefa in tarefas:
            ProcessamentoTarefaMassa.objects.create(
                rodada=rodada,
                tarefa=tarefa
            )

        # 🚦 Marca a primeira tarefa automaticamente
        primeira_tarefa = rodada.tarefas_processadas.filter(
            status='nao_processada',
            tarefa__status__in=['pendente', 'em_andamento']
        ).first()

        if primeira_tarefa:
            primeira_tarefa.status = 'em_processamento'
            primeira_tarefa.processado_por = request.user
            primeira_tarefa.save()

            return redirect(f"{reverse('app_tarefas:single_tarefa', kwargs={'pk': primeira_tarefa.tarefa.pk})}?rodada_id={rodada.pk}")

        # Caso não haja tarefas válidas
        messages.info(request, "Nenhuma tarefa disponível para processar.")
        return redirect('app_tarefas:gerar_tarefa_massa')



class ProcessarProximaTarefaView(LoginRequiredMixin, View):
    def get(self, request, rodada_id):
        rodada = get_object_or_404(RodadaProcessamentoTarefaMassa, pk=rodada_id)

        try:
            with transaction.atomic():
                tarefa_proc = rodada.tarefas_processadas.select_for_update(skip_locked=True).filter(
                    status='nao_processada',
                    tarefa__status__in=['pendente', 'em_andamento'],
                    processado_por__isnull=True
                ).first()

                if not tarefa_proc:
                    messages.info(request, "Todas as tarefas estão em processamento ou foram concluídas.")
                    return redirect('app_tarefas:gerar_tarefa_massa')


                # ⚠️ CLAIM da tarefa aqui mesmo!
                tarefa_proc.status = 'em_processamento'
                tarefa_proc.processado_por = request.user
                tarefa_proc.save()

                return redirect(
                    f"{reverse('app_tarefas:single_tarefa', kwargs={'pk': tarefa_proc.tarefa.pk})}?rodada_id={rodada.pk}"
                )

        except Exception as e:
            print(f"❌ Erro ao processar tarefa: {str(e)}")
            messages.error(request, "Erro ao acessar próxima tarefa.")
            return redirect('app_tarefas:gerar_tarefa_massa')


# Deletar tarefas em massa
class TarefaMassaDeleteView(LoginRequiredMixin, DeleteView):
    model = TarefaMassaModel
    template_name = 'app_tarefas/delete_tarefa_massa.html'
    context_object_name = 'massa'
    success_url = reverse_lazy('app_tarefas:gerar_tarefa_massa')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        massa = self.get_object()
        tarefas = massa.tarefas_geradas.all()

        total = tarefas.count()
        concluidas = tarefas.filter(status='concluida').count()
        pendentes = total - concluidas

        context.update({
            'total_tarefas': total,
            'concluidas': concluidas,
            'pendentes': pendentes,
            'pode_deletar': pendentes == 0 or self.request.GET.get('forcar') == '1'
        })

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        tarefas = self.object.tarefas_geradas.all()

        total = tarefas.count()
        concluidas = tarefas.filter(status='concluida').count()
        pendentes = total - concluidas

        # Bloqueia deletar se houver tarefas pendentes e não forçou
        if pendentes > 0 and request.POST.get("forcar") != "1":
            messages.warning(request, "Existem tarefas não concluídas. Confirme a exclusão marcando 'forçar'.")
            return redirect(f"{self.request.path}?forcar=1")

        # Deleta dependências
        tarefas.delete()
        self.object.rodadas.all().delete()

        # Deleta o próprio lançamento
        self.object.delete()
        messages.success(request, "Lançamento e tarefas vinculadas deletadas com sucesso.")
        return redirect(self.success_url)
        
        
# ========= INSS =====Viwes====
# Lista com os associados que recolhem o inss
from django.views.generic import ListView
from .models import LancamentoINSSModel
from datetime import datetime, timedelta

from django.db.utils import IntegrityError

class CriarLancamentoINSSView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = LancamentoINSSModel
    form_class = LancamentoINSSForm
    template_name = 'app_tarefas/create_lancamentoInss.html'
    success_url = reverse_lazy('app_tarefas:list_lancamentos')
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
        return {
            'ano': now().year,
            'mes': now().month,
            'criado_por': self.request.user  # <-- Aqui!            
        }
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meses_nomes'] = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        return context
    
    def form_valid(self, form):
        form.instance.criado_por = self.request.user

        try:
            lancamento, created, guias_criadas = LancamentoINSSModel.gerar_lancamento(
                ano=form.instance.ano,
                mes=form.instance.mes,
                user=self.request.user
            )

            if created:
                messages.success(
                    self.request,
                    f"Lançamento {form.instance.mes:02d}/{form.instance.ano} criado com sucesso com {guias_criadas} guias."
                )
                return redirect(self.success_url)  # ✅ Evita super().form_valid()

            elif guias_criadas > 0:
                messages.info(
                    self.request,
                    f"Lançamento já existia. {guias_criadas} guias foram adicionadas."
                )
            else:
                messages.warning(
                    self.request,
                    "Este lançamento já existia e nenhuma nova guia foi adicionada."
                )

            return self.render_to_response(self.get_context_data(form=form))

        except ValueError as e:
            messages.error(self.request, str(e))
            return self.render_to_response(self.get_context_data(form=form))

        except IntegrityError:
            messages.error(
                self.request,
                f"⚠️ Já existe um lançamento para {form.instance.mes:02d}/{form.instance.ano}."
            )
            return self.render_to_response(self.get_context_data(form=form))



class LancamentoINSSListView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = LancamentoINSSModel
    template_name = 'app_tarefas/list_lancamentos.html'
    context_object_name = 'lancamentos'
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
        queryset = super().get_queryset()
        ano = self.request.GET.get('ano')
        mes = self.request.GET.get('mes')

        if ano:
            queryset = queryset.filter(ano=ano)
        if mes:
            queryset = queryset.filter(mes=mes)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano_atual = datetime.now().year

        # Anos: do atual até 2020, decrescente
        context['anos_disponiveis'] = list(range(ano_atual, 2023, -1))

        # Meses válidos (04 a 11)
        context['meses_disponiveis'] = [(i, f'{i:02d}') for i in range(4, 12)]

        return context


# Views
class GerarLancamentoINSSView(LoginRequiredMixin, GroupPermissionRequiredMixin, View):
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]
    def post(self, request, *args, **kwargs):
        try:
            ano = int(request.POST.get('ano'))
            mes = int(request.POST.get('mes'))
            
            lancamento, created, total_guias = LancamentoINSSModel.gerar_lancamento(
                ano, mes, request.user
            )

            if created:
                msg = f"Lançamento {mes:02d}/{ano} criado com sucesso. {total_guias} guias geradas."
                messages.success(request, msg)
            elif total_guias > 0:
                msg = f"Lançamento {mes:02d}/{ano} já existia. {total_guias} novas guias adicionadas."
                messages.info(request, msg)
            else:
                msg = f"Lançamento {mes:02d}/{ano} já existia com todas guias."
                messages.warning(request, msg)
                
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Erro ao gerar lançamento: {str(e)}")


        return redirect('app_tarefas:list_lancamentos')
    
    
    

class DetalheLancamentoINSSView(LoginRequiredMixin, GroupPermissionRequiredMixin, DetailView):
    model = LancamentoINSSModel
    template_name = 'app_tarefas/detalhe_lancamento.html'
    context_object_name = 'lancamento'
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
        lancamento = self.object

        # 🔎 Recupera os filtros da URL
        nome_query = self.request.GET.get('q', '').strip()
        status_filtro = self.request.GET.get('status', '')
        observacao_filtro = self.request.GET.get('obs', '')

        # 🔁 Queryset base com o select_related
        guias = lancamento.guias.select_related('associado', 'associado__user')

        # 🔤 Filtrar por nome
        if nome_query:
            guias = guias.filter(
                Q(associado__user__first_name__icontains=nome_query) |
                Q(associado__user__last_name__icontains=nome_query)
            )

        # ✅ Filtrar por status
        if status_filtro:
            guias = guias.filter(status=status_filtro)

        # ✅ Filtrar por observação
        if observacao_filtro:
            guias = guias.filter(observacoes=observacao_filtro)

        # 🔠 Ordena por nome completo
        guias = guias.order_by('associado__user__first_name', 'associado__user__last_name')

        context['guias'] = guias
        context['status_choices'] = GuiaINSSModel.get_status_choices()
        context['observacoes_choices'] = GuiaINSSModel.get_observacoes_choices()
        context['nome_query'] = nome_query
        context['status_filtro'] = status_filtro
        context['observacao_filtro'] = observacao_filtro

        return context

from django.contrib import messages
from django.shortcuts import redirect

@require_POST
def atualizar_guia(request, guia_id):
    guia = get_object_or_404(GuiaINSSModel, id=guia_id)

    status = request.POST.get('status')
    observacoes = request.POST.get('observacoes')

    if status:
        guia.status = status

    if observacoes:
        guia.observacoes = observacoes

    guia.save()

    messages.success(request, f"Guia de {guia.associado} atualizada com sucesso!")

    return redirect(request.META.get('HTTP_REFERER', '/'))


class ProcessarGuiaView(LoginRequiredMixin, GroupPermissionRequiredMixin, View):
    template_name = 'app_tarefas/processar_guia.html'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]    

    def get(self, request, lancamento_id):
        User = get_user_model()
        lancamento = get_object_or_404(LancamentoINSSModel, id=lancamento_id)

        rodada, created = RodadaProcessamentoINSS.objects.get_or_create(
            lancamento=lancamento,
            ativa=True,
            defaults={'iniciada_em': now()}
        )

        # 🔓 Limpa guias travadas
        tempo_expiracao = now() - timedelta(minutes=15)
        lancamento.guias.filter(
            em_processamento_por__isnull=False,
            iniciou_em__lt=tempo_expiracao
        ).update(em_processamento_por=None, iniciou_em=None)

        # 📌 Guias processadas
        guias_processadas_ids = GuiaRodadaProcessada.objects.filter(
            rodada=rodada
        ).values_list('guia_id', flat=True)

        # 📍 Guias disponíveis
        guias_disponiveis = GuiaINSSModel.objects.filter(
            lancamento=lancamento,
            status='pendente'
        ).exclude(
            id__in=guias_processadas_ids
        ).filter(
            Q(em_processamento_por__isnull=True) | Q(iniciou_em__lt=tempo_expiracao)
        ).select_related('associado__user').order_by('id')

        # 👥 Participantes (pegando processado_por)
        usuarios_participantes_ids = GuiaRodadaProcessada.objects.filter(
            rodada=rodada
        ).exclude(processado_por__isnull=True).values_list('processado_por', flat=True).distinct()

        usuarios_participantes = User.objects.filter(id__in=usuarios_participantes_ids)

        guia = None
        current_guia_id = request.GET.get('guia')
        if current_guia_id:
            guia = guias_disponiveis.filter(id=current_guia_id).first()
        else:
            progresso = ProgressoGuiaINSSModel.objects.filter(user=request.user, lancamento=lancamento).first()
            if progresso:
                guia = guias_disponiveis.filter(id=progresso.ultima_guia_id).first()
            if not guia:
                guia = guias_disponiveis.first()

        if not guia and guias_disponiveis.exists():
            return render(request, self.template_name, {
                'aguarde': True,
                'lancamento': lancamento,
                'fim_processo': False,
                'rodada': rodada,
                
            })

        if not guia:
            rodada.ativa = False
            rodada.finalizada_em = now()
            rodada.save()
            request.session.pop(f'ultima_guia_{lancamento_id}', None)
            return render(request, self.template_name, {
                'guia': None,
                'lancamento': lancamento,
                'fim_processo': True,
                'rodada': rodada,
            })

        guia.em_processamento_por = request.user
        guia.iniciou_em = now()
        guia.save()

        guia_ids = list(guias_disponiveis.values_list('id', flat=True))
        try:
            current_index = guia_ids.index(guia.id)
            next_guia_id = guia_ids[current_index + 1] if current_index + 1 < len(guia_ids) else None
        except ValueError:
            current_index = 0
            next_guia_id = None

        contador = GuiaRodadaProcessada.objects.filter(rodada=rodada).count() + 1
        total_guias = GuiaINSSModel.objects.filter(lancamento=lancamento).count()

        guias_anteriores = GuiaINSSModel.objects.filter(
            associado=guia.associado,
            lancamento__ano=lancamento.ano,
            lancamento__mes__lt=lancamento.mes
        ).select_related('lancamento').order_by('-lancamento__ano', '-lancamento__mes')

        mes_nome = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }.get(lancamento.mes, '')

        processadas = GuiaRodadaProcessada.objects.filter(rodada=rodada).count()
        em_processamento = GuiaINSSModel.objects.filter(
            lancamento=lancamento,
            em_processamento_por__isnull=False
        ).exclude(id__in=guias_processadas_ids).count()
        pendentes = total_guias - processadas - em_processamento

        percentual = 0
        if total_guias > 0:
            percentual = (processadas / total_guias) * 100
            
        # 📊 Estatísticas de status (novo)
        status_counts = GuiaINSSModel.objects.filter(
            lancamento=lancamento
        ).values('status').annotate(
            total=Count('id')
        ).order_by('status')

        # Transforma em um dicionário mais fácil de usar no template
        status_distribuicao = {
            item['status']: item['total'] 
            for item in status_counts
        }
            
        return render(request, self.template_name, {
            'guia': guia,
            'lancamento': lancamento,
            'status_choices': GuiaINSSModel.get_status_choices(),
            'observacoes_choices': GuiaINSSModel.get_observacoes_choices(),
            'next_guia_id': next_guia_id,
            'guias_anteriores': guias_anteriores,
            'contador': contador,
            'total_guias': total_guias,
            'mes_nome': mes_nome,
            'total': total_guias,
            'processadas': processadas,
            'em_processamento': em_processamento,
            'pendentes': pendentes,
            'rodada': rodada,
            'usuarios_participantes': usuarios_participantes,
            'percentual': percentual,
            'status_distribuicao': status_distribuicao,
            'status_choices_dict': dict(GuiaINSSModel.STATUS_CHOICES),
        })


    def post(self, request, lancamento_id):
        guia_id = request.POST.get('guia_id')
        guia = get_object_or_404(GuiaINSSModel, id=guia_id)

        # 1️⃣ VALIDAÇÃO DO STATUS RECEBIDO
        status_recebido = request.POST.get('status')
        status_validos = dict(GuiaINSSModel.STATUS_CHOICES).keys()
        
        if status_recebido not in status_validos:
            messages.error(request, "Status inválido selecionado.")
            return redirect(f"{request.path}?guia={guia_id}")

        # Registrar guia como processada nesta rodada
        rodada = RodadaProcessamentoINSS.objects.filter(lancamento_id=lancamento_id, ativa=True).first()
        if rodada:
            gpp, created = GuiaRodadaProcessada.objects.get_or_create(
                rodada=rodada,
                guia=guia,
                defaults={'user': request.user, 'processado_por': request.user}
            )
            if not created:
                gpp.user = request.user
                gpp.processado_por = request.user
                gpp.save()

        # Salva a guia atual (agora com status validado)
        guia.status = status_recebido
        guia.observacoes = request.POST.get('observacoes') or 'certo'
        guia.save()

        # Registrar guia como processada
        GuiaRodadaProcessada.objects.get_or_create(
            rodada=rodada,
            guia=guia,
            defaults={
                'user': guia.associado.user,
                'processado_por': request.user,
            }
        )

        # Atualiza guias anteriores (com validação de status)
        for key in request.POST:
            if key.startswith("status_anterior_"):
                guia_anterior_id = key.replace("status_anterior_", "")
                status_val = request.POST.get(key)
                observacoes_val = request.POST.get(f"obs_anterior_{guia_anterior_id}")

                if status_val in status_validos:  # Só atualiza se status for válido
                    try:
                        g = GuiaINSSModel.objects.get(id=guia_anterior_id)
                        g.status = status_val
                        g.observacoes = observacoes_val or 'certo'
                        g.save()
                    except GuiaINSSModel.DoesNotExist:
                        continue

        # Libera a guia
        guia.em_processamento_por = None
        guia.iniciou_em = None
        guia.save()

        # Salva ponto de parada
        ProgressoGuiaINSSModel.objects.update_or_create(
            user=request.user,
            lancamento_id=lancamento_id,
            defaults={'ultima_guia': guia}
        )

        # Verifica conclusão
        total_guias = GuiaINSSModel.objects.filter(lancamento_id=lancamento_id).count()
        guias_processadas = GuiaRodadaProcessada.objects.filter(rodada=rodada).count()

        if guias_processadas >= total_guias:
            rodada.ativa = False
            rodada.finalizada_em = now()
            rodada.save()

        if request.POST.get('acao') == 'pausar':
            messages.info(request, "Processamento pausado.")
            return redirect('app_tarefas:list_lancamentos')

        # 🔄 Buscar próxima guia DISPONÍVEL E PENDENTE (modificado)
        tempo_expiracao = now() - timedelta(minutes=15)
        proxima_guia = GuiaINSSModel.objects.filter(
            lancamento_id=lancamento_id,
            status='pendente'  # Filtro adicionado para pegar apenas pendentes
        ).exclude(
            id__in=GuiaRodadaProcessada.objects.filter(rodada=rodada).values_list('guia_id', flat=True)
        ).filter(
            Q(em_processamento_por__isnull=True) | Q(iniciou_em__lt=tempo_expiracao)
        ).order_by('id').first()

        if proxima_guia:
            return redirect(f"{request.path}?guia={proxima_guia.id}")
        else:
            messages.success(request, "Processo de emissão finalizado com sucesso!")
            request.session.pop(f'ultima_guia_{lancamento_id}', None)
            return redirect('app_tarefas:list_lancamentos')
#--------------------------

class LancamentosINSSPorAssociadoView(LoginRequiredMixin, GroupPermissionRequiredMixin, View):
    template_name = 'app_tarefas/lancamento_inss_por_associado.html'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]

    def get(self, request, associado_id):
        associado = get_object_or_404(AssociadoModel, id=associado_id)

        guias = GuiaINSSModel.objects.select_related('lancamento') \
            .filter(associado=associado) \
            .order_by('-lancamento__ano', '-lancamento__mes')

        lancamentos = {}
        for guia in guias:
            key = (guia.lancamento.ano, guia.lancamento.mes)
            lancamentos.setdefault(key, []).append(guia)

        context = {
            'associado': associado,
            'lancamentos': dict(sorted(lancamentos.items(), reverse=True)),
            'status_choices': GuiaINSSModel.get_status_choices(),
            'observacoes_choices': GuiaINSSModel.get_observacoes_choices()
        }
        return render(request, self.template_name, context)

# ====================

#-----------------
# REAPS ANUAL
# Gerar e listar Lançamentos REAPS Anuais
class GerarListarReapsView(LoginRequiredMixin, GroupPermissionRequiredMixin, View):
    template_name = 'app_tarefas/lista_reaps_anuais.html'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]

    def get(self, request):
        reaps_lancamentos = ReapsAnualModel.objects.all().order_by('-ano')
        return render(request, self.template_name, {
            'reaps_lancamentos': reaps_lancamentos
        })

    def post(self, request):
        ano_atual = now().year

        if ReapsAnualModel.objects.filter(ano=ano_atual).exists():
            messages.warning(request, f"⚠️ Já existe um lançamento REAPS para {ano_atual}.")
            return redirect('app_tarefas:lista_reaps')

        reaps = criar_lancamento_reaps(request.user, ano=ano_atual)
        messages.success(request, f"✅ Lançamento REAPS {ano_atual} criado com sucesso.")
        return redirect('app_tarefas:reaps_detalhe', pk=reaps.pk)


 # Detalhe Lançamento REAPS Anual Lista de Intens
class ReapsAssociadosListView(LoginRequiredMixin, GroupPermissionRequiredMixin, DetailView):
    model = ReapsAnualModel
    template_name = 'app_tarefas/detalhe_reaps_ano.html'
    context_object_name = 'reaps'
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
        reaps = self.get_object()

        itens = reaps.itens.select_related('associado__user').order_by(
            'associado__user__first_name',
            'associado__user__last_name'
        )

        context.update({
            'itens': itens,
            'total': reaps.total_itens(),
            'concluidos': reaps.total_processados(),
            'pendentes': reaps.total_pendentes(),
            'processando': reaps.total_em_processamento(),
        })
        return context

# Gerar Procesar REAPS Individual    
class ReapsProcessarView(LoginRequiredMixin, GroupPermissionRequiredMixin, DetailView):
    model = ReapsAssociadoItem
    template_name = 'app_tarefas/processar_reaps_individual.html'
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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        acao = request.POST.get('acao')
        reaps = self.object.reaps

        # Sessões da rodada
        session_key_visitados = f"reaps_visitados_{reaps.pk}"
        session_key_pulados = f"reaps_pulados_{reaps.pk}"

        visitados = request.session.get(session_key_visitados, [])
        pulados = request.session.get(session_key_pulados, [])

        # Adiciona atual aos visitados
        if self.object.pk not in visitados:
            visitados.append(self.object.pk)
            request.session[session_key_visitados] = visitados

        # AÇÕES DE USUÁRIO
        if acao in ['concluir', 'concluir_proximo']:
            self.object.status = 'CONCLUIDO'
            self.object.data_realizado = now().date()
            self.object.processado_por = request.user
            self.object.save()
            messages.success(request, f"✅ REAPS de {self.object.associado.user.get_full_name()} concluído com sucesso.")

        elif acao == 'pular_proximo':
            self.object.status = 'PENDENTE'
            self.object.processado_por = None
            self.object.pulado_na_rodada = True  # 🔁 Persistente no banco
            self.object.save()

            if self.object.pk not in pulados:
                pulados.append(self.object.pk)
                request.session[session_key_pulados] = pulados

            messages.info(request, "⏭️ Item retornado para pendente e indo para o próximo.")

        elif acao == 'pausar':
            self.object.status = 'PENDENTE'
            self.object.processado_por = None
            self.object.data_realizado = None
            self.object.save()
            messages.info(request, "⏸️ REAPS pausado.")

        elif acao == 'iniciar':
            if self.object.status != 'CONCLUIDO' and (self.object.status != 'PROCESSANDO' or self.object.processado_por is None):
                self.object.status = 'PROCESSANDO'
                self.object.processado_por = request.user
                self.object.save()
                messages.info(request, "🔄 Iniciado o processamento do REAPS.")
            else:
                messages.warning(request, "⚠️ Este item já está em processamento por outro usuário.")

        # Lógica para avançar para próximo
        if acao in ['concluir_proximo', 'pular_proximo']:
            proximo_item = (
                ReapsAssociadoItem.objects
                .filter(
                    reaps=reaps,
                    status='PENDENTE',
                    pulado_na_rodada=False
                )
                .exclude(pk__in=visitados + pulados)
                .exclude(Q(status='PROCESSANDO') & ~Q(processado_por=request.user))
                .order_by('associado__user__first_name', 'associado__user__last_name')
                .first()
            )

            if proximo_item:
                updated = ReapsAssociadoItem.objects.filter(
                    pk=proximo_item.pk,
                    status='PENDENTE'
                ).update(
                    status='PROCESSANDO',
                    processado_por=request.user
                )

                if updated:
                    return redirect(
                        f"{reverse('app_tarefas:processar_reaps', kwargs={'pk': proximo_item.pk})}?pela_rodada=1"
                    )
                else:
                    messages.warning(request, "⚠️ Outro usuário começou a processar esse item.")

            # ✅ Final da rodada
            # ✅ Remove sessão do usuário
            request.session.pop(session_key_visitados, None)
            request.session.pop(session_key_pulados, None)

            # 🔍 Verifica se ainda há usuários processando
            tem_usuarios_processando = ReapsAssociadoItem.objects.filter(
                reaps=reaps,
                status='PROCESSANDO'
            ).exists()

            if not tem_usuarios_processando:
                # 🔚 Rodada ENCERRADA para todos
                ReapsAssociadoItem.objects.filter(
                    reaps=reaps,
                    pulado_na_rodada=True
                ).update(pulado_na_rodada=False)

                messages.info(request, "🎉 Todos os usuários concluíram. Rodada finalizada.")

            else:
                messages.info(request, "✅ Você finalizou sua rodada. Outros usuários ainda estão processando.")

            return redirect('app_tarefas:reaps_detalhe', pk=reaps.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        associado = self.object.associado
        reaps = self.object.reaps

        usuarios_ativos = User.objects.filter(
            reaps_processados__reaps=reaps,
            reaps_processados__status='PROCESSANDO'
        ).distinct()

        context.update({
            'associado_user': associado.user,
            'cpf': associado.cpf,
            'senha_gov': associado.senha_gov,
            'relacao_trabalho': associado.relacao_trabalho,
            'comercializa_produtos': associado.comercializa_produtos,
            'bolsa_familia': associado.bolsa_familia,
            'pela_rodada': self.request.GET.get('pela_rodada') == '1',
            'usuarios_processando': usuarios_ativos,
        })
        return context


@login_required
def iniciar_reaps_rodada_view(request, pk):
    reaps = get_object_or_404(ReapsAnualModel, pk=pk)

    # 🔁 Limpa histórico da rodada atual na sessão
    session_key_visitados = f"reaps_visitados_{reaps.pk}"
    session_key_pulados = f"reaps_pulados_{reaps.pk}"
    request.session.pop(session_key_visitados, None)
    request.session.pop(session_key_pulados, None)

    try:
        with transaction.atomic():
            proximo_item = (
                ReapsAssociadoItem.objects
                .select_related('associado__user')
                .filter(
                    reaps=reaps,
                    status='PENDENTE',
                    pulado_na_rodada=False  # 🛡️ ESSENCIAL: evita reaparecimento dos pulados
                )
                .exclude(
                    Q(status='PROCESSANDO') & ~Q(processado_por=request.user)
                )
                .order_by(
                    'associado__user__first_name',
                    'associado__user__last_name'
                )
                .first()
            )

            if proximo_item:
                updated = ReapsAssociadoItem.objects.filter(
                    pk=proximo_item.pk,
                    status='PENDENTE'
                ).update(
                    status='PROCESSANDO',
                    processado_por=request.user
                )

                if updated:
                    return redirect(
                        f"{reverse('app_tarefas:processar_reaps', kwargs={'pk': proximo_item.pk})}?pela_rodada=1"
                    )
                else:
                    messages.warning(request, "⚠️ Outro usuário já iniciou o processamento deste item.")
                    return redirect('app_tarefas:reaps_detalhe', pk=reaps.pk)

    except Exception as e:
        messages.error(request, f"❌ Erro ao iniciar rodada: {str(e)}")
        return redirect('app_tarefas:reaps_detalhe', pk=reaps.pk)

    messages.info(request, "🎉 Todos os itens disponíveis já estão sendo processados ou concluídos.")
    return redirect('app_tarefas:reaps_detalhe', pk=reaps.pk)


class ReapsDeleteView(LoginRequiredMixin, GroupPermissionRequiredMixin, View):
    template_name = 'app_tarefas/delete_reaps.html'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
    ]    
    
    def get(self, request, pk):
        reaps = get_object_or_404(ReapsAnualModel, pk=pk)
        pendentes = reaps.itens.filter(status='PENDENTE').count()
        concluidos = reaps.itens.filter(status='CONCLUIDO').count()
        total = reaps.itens.count()

        context = {
            'reaps': reaps,
            'pendentes': pendentes,
            'concluidos': concluidos,
            'total': total,
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        reaps = get_object_or_404(ReapsAnualModel, pk=pk)
        pendentes = reaps.itens.filter(status='PENDENTE').count()

        if pendentes > 0:
            messages.warning(request, f"⚠️ Ainda há {pendentes} REAPS pendentes.")
        else:
            messages.success(request, f"✅ Lançamento REAPS {reaps.ano} deletado com sucesso.")

        # Deleta os itens e o lançamento
        reaps.itens.all().delete()
        reaps.delete()

        return redirect('app_tarefas:lista_reaps')