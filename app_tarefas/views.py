from django.shortcuts import render, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib import messages
from django.utils.timezone import now, timezone
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import GroupPermissionRequiredMixin
from django.contrib.auth.models import Group
from .models import TarefaModel, HistoricoStatusModel, HistoricoResponsaveisModel, ProgressoGuiaINSSModel
from .forms import TarefaForm, LancamentoINSSForm
from django.urls import reverse_lazy, reverse
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
from .models import LancamentoINSSModel, GuiaINSSModel
from django.template.loader import render_to_string
from django.utils import timezone
from decimal import Decimal
from django.views.decorators.http import require_POST
from django.db import IntegrityError
import calendar

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

    def post(self, request, pk):
        tarefa = get_object_or_404(TarefaModel, pk=pk)

        # Atualizar responsáveis se vier do form de responsáveis
        if 'responsaveis' in request.POST:
            novos_responsaveis = request.POST.getlist('responsaveis')
            tarefa.responsaveis.set(novos_responsaveis)
            messages.success(request, "Responsáveis atualizados com sucesso!")

        # Atualizar checklist
        for item in tarefa.checklist_itens.all():
            checkbox_name = f"item_{item.id}"
            item.concluido = checkbox_name in request.POST
            item.save()

        messages.success(request, "Checklist atualizado com sucesso.")
        return redirect('app_tarefas:single_tarefa', pk=tarefa.pk)
    
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


        # ✔️ Progresso do checklist da tarefa atual
        checklist = self.object.checklist_itens.all()
        total = checklist.count()
        feitos = checklist.filter(concluido=True).count()
        progresso_percentual = int((feitos / total) * 100) if total > 0 else 0

        context.update({
            'total_itens': total,
            'feitos_itens': feitos,
            'progresso': progresso_percentual,
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




# ========= INSS =====Viwes====
# Lista com os associados que recolhem o inss
from django.views.generic import ListView
from .models import LancamentoINSSModel
from datetime import datetime

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


from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from .models import GuiaINSSModel, LancamentoINSSModel

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
        lancamento = get_object_or_404(LancamentoINSSModel, id=lancamento_id)
        guias = lancamento.guias.select_related('associado').order_by('id')

        current_guia_id = request.GET.get('guia')
        guia = None
        if current_guia_id:
            guia = guias.filter(id=current_guia_id).first()
        else:
            progresso = ProgressoGuiaINSSModel.objects.filter(
                user=request.user,
                lancamento=lancamento
            ).first()

            if progresso:
                guia = guias.filter(id=progresso.ultima_guia_id).first()
            else:
                guia = guias.first()

        if not guia:
            request.session.pop(f'ultima_guia_{lancamento_id}', None)
            return render(request, self.template_name, {
                'guia': None,
                'lancamento': lancamento,
                'fim_processo': True,
            })

        # ✅ Agora que `guia` existe, podemos montar guia_ids e index
        guia_ids = list(g.id for g in guias)

        try:
            current_index = guia_ids.index(guia.id)
            next_guia_id = guia_ids[current_index + 1] if current_index + 1 < len(guia_ids) else None
        except ValueError:
            current_index = 0
            next_guia_id = None

        total_guias = len(guia_ids)
        contador = current_index + 1

        # 👇 Guias anteriores
        guias_anteriores = GuiaINSSModel.objects.filter(
            associado=guia.associado,
            lancamento__ano=lancamento.ano,
            lancamento__mes__lt=lancamento.mes
        ).select_related('lancamento').order_by('-lancamento__ano', '-lancamento__mes')

        MESES_PT = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        mes_nome = MESES_PT.get(lancamento.mes, '')

        return render(request, self.template_name, {
            'guia': guia,
            'lancamento': lancamento,
            'status_choices': GuiaINSSModel.get_status_choices(),
            'observacoes_choices': GuiaINSSModel.get_observacoes_choices(),
            'next_guia_id': next_guia_id,
            'guias_anteriores': guias_anteriores,
            'contador': contador,
            'total_guias': total_guias,
            'mes_nome': mes_nome,  # 👈 Aqui o que faltava
            
        })


    def post(self, request, lancamento_id):
        guia_id = request.POST.get('guia_id')
        guia = get_object_or_404(GuiaINSSModel, id=guia_id)

        # Salva a guia atual
        guia.status = request.POST.get('status')
        guia.observacoes = request.POST.get('observacoes') or 'certo'

        guia.save()

        # 🔁 Atualiza guias anteriores, se vieram no form
        for key in request.POST:
            if key.startswith("status_anterior_"):
                guia_anterior_id = key.replace("status_anterior_", "")
                status_val = request.POST.get(key)
                observacoes_val = request.POST.get(f"obs_anterior_{guia_anterior_id}")

                try:
                    g = GuiaINSSModel.objects.get(id=guia_anterior_id)
                    g.status = status_val
                    g.observacoes = observacoes_val or 'certo'
                    g.save()
                except GuiaINSSModel.DoesNotExist:
                    continue

        # Salva ponto de parada
        ProgressoGuiaINSSModel.objects.update_or_create(
            user=request.user,
            lancamento_id=lancamento_id,
            defaults={'ultima_guia': guia}
        )

        if request.POST.get('acao') == 'pausar':
            messages.info(request, "Processamento pausado.")
            return redirect('app_tarefas:list_lancamentos')

        next_guia_id = request.POST.get('next_guia_id')
        if next_guia_id and next_guia_id != "None":
            return redirect(f"{request.path}?guia={next_guia_id}")
        else:
            request.session.pop(f'ultima_guia_{lancamento_id}', None)
            messages.success(request, "Processo de emissão finalizado com sucesso!")
            return redirect('app_tarefas:list_lancamentos')




