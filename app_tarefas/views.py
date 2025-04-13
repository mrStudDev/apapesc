from django.shortcuts import render, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib import messages
from django.utils.timezone import now, timezone
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import GroupPermissionRequiredMixin
from django.contrib.auth.models import Group
from .models import TarefaModel, HistoricoStatusModel, HistoricoResponsaveisModel
from .forms import TarefaForm
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
from .models import GuiaINSSModel
from django.template.loader import render_to_string
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
# Lista com os associados que recolhem o inss
class EmissaoGuiasView(LoginRequiredMixin, TemplateView):
    template_name = "app_tarefas/emissao_guias.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        ano_selecionado = int(self.request.GET.get("ano", now().year))
        ano_atual = now().year
        meses_validos = list(range(4, 12))  # Abril a Novembro
        termo_busca = self.request.GET.get("busca", "")

        # Query base já ordenada por sobrenome e nome
        associados_query = AssociadoModel.objects.filter(
            recolhe_inss="Sim"
        ).select_related('user').order_by(
           'user__first_name',            
            'user__last_name'
        )

        # Aplica filtro de busca se existir
        if termo_busca:
            associados_query = associados_query.filter(
                Q(user__first_name__icontains=termo_busca) |
                Q(user__last_name__icontains=termo_busca)
            )

        # Lista ordenada de associados
        associados_ordenados = list(associados_query)
        
        # Prepara a estrutura de dados mantendo a ordenação original
        guias_por_associado = {}
        for associado in associados_ordenados:
            # Verifica se o associado pode ter guias no ano selecionado
            ano_filiacao = associado.data_filiacao.year if associado.data_filiacao else ano_atual
            if ano_selecionado < ano_filiacao:
                continue  # Pula associados filiados após o ano selecionado

            guias = {mes: None for mes in meses_validos}
            guias_existentes = GuiaINSSModel.objects.filter(
                associado=associado, 
                ano=ano_selecionado
            )

            for guia in guias_existentes:
                guias[guia.mes_referencia] = guia

            guias_por_associado[associado.id] = {
                "dados": {
                    "id": associado.id,
                    "user__first_name": associado.user.first_name,
                    "user__last_name": associado.user.last_name,
                    "cpf": associado.cpf,
                    "senha_gov": associado.senha_gov,
                    "celular_correspondencia": associado.celular_correspondencia,
                    "nome_completo": f"{associado.user.last_name} {associado.user.first_name}",
                    "ano_filiacao": ano_filiacao  # Adicionado para referência
                },
                "guias": guias
            }

        # Calcula anos disponíveis considerando a filiação mais antiga
        anos_disponiveis = range(2022, ano_atual + 1)
        if associados_ordenados:
            primeiro_ano = min(assoc.data_filiacao.year if assoc.data_filiacao else ano_atual 
                             for assoc in associados_ordenados)
            anos_disponiveis = range(max(2022, primeiro_ano), ano_atual + 1)

        context.update({
            "ano_selecionado": ano_selecionado,
            "anos_disponiveis": anos_disponiveis,
            "meses_validos": meses_validos,
            "guias_por_associado": guias_por_associado,
            "termo_busca": termo_busca,
        })
        return context

# Lógica para processo de emissão
class CriarGuiaView(LoginRequiredMixin, View):
    def post(self, request, associado_id, mes, ano):
        associado = get_object_or_404(AssociadoModel, id=associado_id)
        
        if GuiaINSSModel.objects.filter(associado=associado, mes_referencia=mes, ano=ano).exists():
            return JsonResponse({
                'success': False,
                'message': 'Já existe uma guia para este período'
            }, status=400)

        guia = GuiaINSSModel.objects.create(
            associado=associado,
            mes_referencia=mes,
            ano=ano,
            emitido_por=request.user,
            status="pendente"  # Inicia como pendente
        )

        # HTML para o estado pendente
        html = f"""
        <div class="guia-pendente">
            <!-- DIV de dados separada do formulário -->
            <div class="dados-associado mt-2 space-y-1 bg-yellow-50 p-2 rounded-md shadow-inner text-left">
                <div class="flex justify-between items-center">
                    <span id="cpf-{associado.id}" class="text-gray-800 font-mono text-[11px]">{associado.cpf}</span>
                    <button type="button" data-copy-target="cpf-{associado.id}" 
                            class="btn-copiar text-blue-600 hover:text-blue-800 text-xs focus:outline-none">📋</button>
                </div>
                <div class="flex justify-between items-center">
                    <span id="senha-{associado.id}" class="text-gray-800 font-mono text-[11px]">{associado.senha_gov}</span>
                    <button type="button" data-copy-target="senha-{associado.id}" 
                            class="btn-copiar text-blue-600 hover:text-blue-800 text-xs focus:outline-none">📋</button>
                </div>
                <div class="flex justify-between items-center">
                    <span id="nome-{associado.id}" class="text-gray-800 font-mono text-[11px]">{associado.user.first_name}</span>
                    <button type="button" data-copy-target="nome-{associado.id}" 
                            class="btn-copiar text-blue-600 hover:text-blue-800 text-xs focus:outline-none">📋</button>
                </div>
                <div class="flex justify-between items-center">
                    <span id="texto-guia-{associado.id}" class="text-gray-800 font-mono text-[11px]">
                        Guia INSS - ♥ Apapesc
                    </span>
                    <button type="button" data-copy-target="texto-guia-{associado.id}" 
                            class="btn-copiar text-blue-600 hover:text-blue-800 text-xs focus:outline-none">📋</button>
                </div>                
            </div>

            <!-- Formulário separado -->
            <form method="post" class="form-avancar-status mt-2" 
                  action="{reverse('app_tarefas:atualizar_status_guia', args=[guia.id])}">
                <input type="hidden" name="csrfmiddlewaretoken" value="{request.META['CSRF_COOKIE']}">
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1 rounded shadow transition">
                    Confirmar Emissão (Etapa 1)
                </button>
            </form>
            
            <form method="post" class="form-reiniciar-guia mt-1" 
                  action="{reverse('app_tarefas:zerar_status_guia', args=[guia.id])}">
                <input type="hidden" name="csrfmiddlewaretoken" value="{request.META['CSRF_COOKIE']}">
                <button type="submit" class="w-full text-xs text-red-500 hover:text-red-700 underline">
                    🔄 Reiniciar Processo
                </button>
            </form>
        </div>
        """

        return JsonResponse({
            'success': True,
            'html': html,
            'guia_id': guia.id,
            'reload': True 
        })

# Atualização do Status - parte da Lógica
class AtualizarStatusGuiaView(LoginRequiredMixin, View):
    def post(self, request, guia_id):
        try:
            guia = get_object_or_404(GuiaINSSModel, id=guia_id)
            associado = guia.associado
            
            # Lógica de transição de status corrigida
            if guia.status == "pendente":
                guia.status = "emitido"
                html = self._html_emitido(guia, associado, request)
                message = "Emissão confirmada! Proceda com o envio."
            elif guia.status == "emitido":
                guia.status = "enviado"
                html = self._html_enviado(guia, associado, request)
                message = "Envio confirmado! Aguarde confirmação de pagamento."
            elif guia.status == "enviado":
                guia.status = "pago"
                html = self._html_pago(guia, associado, request)
                message = "Pagamento confirmado! Processo finalizado."
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Status inválido para transição'
                }, status=400)
            
            guia.save()
            
            return JsonResponse({
                'success': True,
                'html': html,
                'message': message,
                'reload': True 
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao atualizar: {str(e)}'
            }, status=400)

    def _html_emitido(self, guia, associado, request):
        return f"""
        <div class="guia-emitida">
            <div class="dados-celular mt-2 bg-green-50 p-2 rounded-md shadow-inner text-left">
                <div class="flex justify-between items-center">
                    <span id="celular-{associado.id}" class="text-gray-800 font-mono text-[11px]">{associado.celular_correspondencia}</span>
                    <button type="button" data-copy-target="celular-{associado.id}" 
                            class="btn-copiar text-blue-600 hover:text-blue-800 text-xs focus:outline-none">📋</button>
                </div>
            </div>

            <form method="post" class="form-avancar-status mt-2" 
                  action="{reverse('app_tarefas:atualizar_status_guia', args=[guia.id])}">
                <input type="hidden" name="csrfmiddlewaretoken" value="{request.META['CSRF_COOKIE']}">
                <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white text-xs px-3 py-1 rounded shadow transition">
                    Confirmar Envio (Etapa 2)
                </button>
            </form>
            
            <form method="post" class="form-reiniciar-guia mt-1" 
                  action="{reverse('app_tarefas:zerar_status_guia', args=[guia.id])}">
                <input type="hidden" name="csrfmiddlewaretoken" value="{request.META['CSRF_COOKIE']}">
                <button type="submit" class="w-full text-xs text-red-500 hover:text-red-700 underline">
                    🔄 Reiniciar Processo
                </button>
            </form>
        </div>
        """

    def _html_enviado(self, guia, associado, request):
        return f"""
        <div class="guia-enviada">
            <p class="text-green-600 text-xs mb-2">Guia enviada ao associado!</p>
            
            <form method="post" class="form-avancar-status" 
                  action="{reverse('app_tarefas:atualizar_status_guia', args=[guia.id])}">
                <input type="hidden" name="csrfmiddlewaretoken" value="{request.META['CSRF_COOKIE']}">
                <button type="submit" class="w-full bg-orange-500 hover:bg-orange-600 text-white text-xs px-3 py-1 rounded shadow transition">
                    Confirmar Pagamento (Etapa 3)
                </button>
            </form>
            
            <form method="post" class="form-reiniciar-guia mt-1" 
                  action="{reverse('app_tarefas:zerar_status_guia', args=[guia.id])}">
                <input type="hidden" name="csrfmiddlewaretoken" value="{request.META['CSRF_COOKIE']}">
                <button type="submit" class="w-full text-xs text-red-500 hover:text-red-700 underline">
                    🔄 Reiniciar Processo
                </button>
            </form>
        </div>
        """

    def _html_pago(self, guia, associado, request):
        return f"""
        <div class="guia-paga">
            <div class="flex items-center justify-center">
                <span class="inline-flex items-center bg-green-50 text-green-700 px-3 py-1 rounded-full text-xs font-semibold shadow-sm ring-1 ring-green-100">
                    <span class="flex-shrink-0 w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    ✅ Guia Paga!
                </span>
            </div>
            
            <form method="post" class="form-reiniciar-guia mt-2 text-center"
                  action="{reverse('app_tarefas:zerar_status_guia', args=[guia.id])}">
                <input type="hidden" name="csrfmiddlewaretoken" value="{request.META['CSRF_COOKIE']}">
                <button type="submit" class="text-xs text-red-500 hover:text-red-700 underline">
                    🔄 Reiniciar Processo
                </button>
            </form>
        </div>
        """

# Reiniciar - Parte da Lógica
class ZerarStatusGuiaView(LoginRequiredMixin, View):
    def post(self, request, guia_id):
        try:
            guia = get_object_or_404(GuiaINSSModel, id=guia_id)
            associado_id = guia.associado.id
            mes = guia.mes_referencia
            ano = guia.ano
            
            # Deletar permanentemente
            guia.hard_delete()
            
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('app_tarefas:emissao_guias'),  # Atualize com sua URL
                'message': 'Processo reiniciado com sucesso'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao reiniciar: {str(e)}'
            }, status=400)