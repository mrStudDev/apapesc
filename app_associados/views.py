from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from .models import AssociadoModel
from .forms import AssociadoForm, ProfissaoForm
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from app_associacao.models import AssociacaoModel, ReparticoesModel, MunicipiosModel, IntegrantesModel
from app_associados.models import STATUS_CHOICES
from app_associados.models import AssociadoModel, ProfissoesModel
from app_tarefas.models import TarefaModel, GuiaINSSModel
from app_servicos.models import ServicoAssociadoModel, StatusEtapaChoices
from django.contrib.auth.models import User
from accounts.mixins import GroupPermissionRequiredMixin 
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
from django.utils.timezone import now
from django.contrib.auth.models import Group
from app_documentos.models import Documento
from django.http import QueryDict
from django.http import JsonResponse


logger = logging.getLogger(__name__)

User = get_user_model()

# Cadastrar Associado
class CreateAssociadoView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = AssociadoModel
    form_class = AssociadoForm
    template_name = 'app_associados/create_associado.html'
    success_url = reverse_lazy('app_associados:list_geral_associado')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        
        user_id = self.request.GET.get('user_id')
        if user_id:
            kwargs['user'] = User.objects.get(id=user_id)
        
            # Obtem associação e repartição selecionadas nos filtros
        associacao_id = self.request.GET.get('associacao')
        reparticao_id = self.request.GET.get('reparticao')

        # Busca os objetos de associação e repartição, se fornecidos
        if associacao_id:
            kwargs['associacao'] = get_object_or_404(AssociacaoModel, pk=associacao_id)
        if reparticao_id:
            kwargs['reparticao'] = get_object_or_404(ReparticoesModel, pk=reparticao_id)

       
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.GET.get('user_id')  # Obtém o ID do usuário da URL
        if user_id:
            user = User.objects.get(id=user_id)
            context['user'] = user  # Adiciona o usuário ao contexto

            # Define o valor inicial do campo de e-mail no formulário
            form = context.get('form')
            if form:
                form.initial['email'] = user.email  # Use o objeto `user` corretamente

        # Repassa os dados submetidos para manter valores em caso de erro
        if self.request.method == "POST":
            context['form'] = self.form_class(self.request.POST)
        else:
            context['form'] = self.get_form()

        # Configura querysets para campos relacionados
        context['form'].fields['reparticao'].queryset = ReparticoesModel.objects.all()
        context['form'].fields['municipio_circunscricao'].queryset = MunicipiosModel.objects.all()
        # Adiciona dados de contexto para filtros
        context['associacoes'] = AssociacaoModel.objects.all().order_by('nome_fantasia')
        context['reparticoes'] = ReparticoesModel.objects.order_by('nome_reparticao')

        # Preserva os valores de filtro na página
        context['associacao_selecionada'] = self.request.GET.get('associacao')
        context['reparticao_selecionada'] = self.request.GET.get('reparticao')

        context['municipios'] = MunicipiosModel.objects.all()
        return context

    def form_valid(self, form):
        user_id = self.request.GET.get('user_id')
        if user_id:
            user = User.objects.get(id=user_id)
            form.instance.user = user  # Associa o usuário ao associado

            # Atualiza o e-mail do usuário, se alterado
            user_email = form.cleaned_data.get('email')
            if user_email and user.email != user_email:
                user.email = user_email
                user.save()
                
            # Adiciona o usuário ao grupo "Associados da Associação"
            group, created = Group.objects.get_or_create(name="Associados da Associação")
            user.groups.add(group)  # Adiciona o usuário ao grupo
                                    
        else:
            messages.error(self.request, "Erro: Nenhum usuário selecionado para associação.")
            return self.form_invalid(form)

        self.object = form.save()  # Salva o formulário

        # Adiciona uma mensagem de sucesso
        messages.success(self.request, "Associado salvo com sucesso!")

        # Redireciona com base no botão clicado
        if "save_and_continue" in self.request.POST:
            return redirect(reverse('app_associados:edit_associado', kwargs={'pk': self.object.pk}))
        elif "save_and_view" in self.request.POST:
            return redirect(reverse('app_associados:single_associado', kwargs={'pk': self.object.pk}))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('app_associados:list_geral_associado')


# List Geral Associados View - Apenas Superuser
class ListAssociadosView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = AssociadoModel
    template_name = 'app_associados/list_geral_associado.html'
    context_object_name = 'associados'
    group_required = [
        'Superuser',
        ]
    
    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtros da request
        associacao_id = self.request.GET.get('associacao', '')
        reparticao_id = self.request.GET.get('reparticao', '')
        status = self.request.GET.get('status', '')

        # Aplica os filtros ao queryset
        if associacao_id:
            queryset = queryset.filter(associacao_id=associacao_id)
        if reparticao_id:
            queryset = queryset.filter(reparticao_id=reparticao_id)
        if status:
            queryset = queryset.filter(status=status)

        # Filtro adicional para busca (opcional)
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(cpf__icontains=query)
            )

        return queryset.order_by('user__first_name', 'user__last_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ano_selecionado = now().year
        meses_validos = list(range(4, 12))  # Abril a Novembro
        associados_inss = AssociadoModel.objects.filter(recolhe_inss="Sim").values("id")

        guias_por_associado = {}
        for associado in associados_inss:
            associado_id = associado["id"]
            guias = {mes: None for mes in meses_validos}
            guias_existentes = GuiaINSSModel.objects.filter(associado_id=associado_id, ano=ano_selecionado)

            for guia in guias_existentes:
                guias[guia.mes_referencia] = guia.status

            guias_por_associado[associado_id] = guias




        # Obtem os associados já filtrados
        associados = list(self.get_queryset())

        # IDs de serviços com status ≠ 'arquivado'
        ids_servico = ServicoAssociadoModel.objects.exclude(status_etapa=StatusEtapaChoices.ARQUIVADO) \
            .exclude(associado__isnull=True) \
            .values_list('associado_id', flat=True)

        # IDs de tarefas com status ≠ 'arquivada'
        ids_tarefa = TarefaModel.objects.exclude(status='arquivada') \
            .exclude(associado__isnull=True) \
            .values_list('associado_id', flat=True)

        ids_com_servico = set(ids_servico)
        ids_com_tarefa = set(ids_tarefa)

        for associado in associados:
            associado.tem_servico = associado.id in ids_com_servico
            associado.tem_tarefa = associado.id in ids_com_tarefa

            if associado.celular:
                associado.celular_clean = associado.celular.replace('-', '').replace(' ', '')

        # Atualiza a lista tratada
        context['associados'] = associados

        # Recupera o ID da ASSOCIAÇÂO selecionada
        selected_associacao_id = self.request.GET.get('associacao', '')

        # Adiciona informações dos filtros ao contexto
        context['associacoes'] = AssociacaoModel.objects.all()
        
        # Filtra repartições com base na ASSOCIAÇÂO selecionada
        if selected_associacao_id:
            context['reparticoes'] = ReparticoesModel.objects.filter(associacao_id=selected_associacao_id)
        else:
            context['reparticoes'] = ReparticoesModel.objects.all()

        
        context['status_choices'] = STATUS_CHOICES
        # Passa os valores selecionados para o template
        context['selected_associacao'] = selected_associacao_id
        context['selected_reparticao'] = self.request.GET.get('reparticao', '')
        context['selected_status'] = self.request.GET.get('status', '')

        context['guias_por_associado'] = guias_por_associado
        context['meses_validos'] = meses_validos


        return context

    
# Single Associado View
class SingleAssociadoView(LoginRequiredMixin, GroupPermissionRequiredMixin, DetailView):
    model = AssociadoModel
    template_name = 'app_associados/single_associado.html'
    context_object_name = 'associado'
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
        associado = self.object  # Associado atual

        # Documentos relacionados ao associado
        context['documentos'] = Documento.objects.filter(associado=associado)

        # Tarefas relacionadas ao associado
        context['tarefas'] = TarefaModel.objects.filter(associado=associado).order_by('-data_criacao')
        context['servicos'] = ServicoAssociadoModel.objects.filter(associado=associado).order_by('-data_inicio')
        context['associado'] = associado
        context['drive_folder_id'] = associado.drive_folder_id

        # Verificação adicional
        if associado.drive_folder_id:
            print(f"Drive Folder ID: {associado.drive_folder_id}")
            print(f"Drive Folder Link: https://drive.google.com/drive/folders/{associado.drive_folder_id}")
        else:
            print("Nenhum Drive Folder ID associado.")

        return context


# Editar Associado
class EditAssociadoView(GroupPermissionRequiredMixin, UpdateView):
    model = AssociadoModel
    form_class = AssociadoForm
    template_name = 'app_associados/edit_associado.html'
    context_object_name = 'associado'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        
        user_id = self.request.GET.get('user_id')
        if user_id:
            kwargs['user'] = User.objects.get(id=user_id)
        
            # Obtem associação e repartição selecionadas nos filtros
        associacao_id = self.request.GET.get('associacao')


        # Busca os objetos de associação e repartição, se fornecidos
        if associacao_id:
            kwargs['associacao'] = get_object_or_404(AssociacaoModel, pk=associacao_id)


        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Passar os dados do associado e configurar campos adicionais
        associado = self.get_object()
        if associado.user:
            context['user'] = associado.user  # Dados do usuário associado

        context['form'].fields['reparticao'].queryset = ReparticoesModel.objects.all()
        context['form'].fields['municipio_circunscricao'].queryset = MunicipiosModel.objects.all()

        # Adiciona dados de contexto para filtros
        context['associacoes'] = AssociacaoModel.objects.all().order_by('nome_fantasia')
        context['reparticoes'] = ReparticoesModel.objects.order_by('nome_reparticao')
        # Preserva os valores de filtro na página
        context['associacao_selecionada'] = self.request.GET.get('associacao')
        context['reparticao_selecionada'] = self.request.GET.get('reparticao')

        context['municipios'] = MunicipiosModel.objects.all()
        return context

    def form_valid(self, form):
        # Não altere o campo `user` se ele já existir
        if not form.instance.user:
            user_id = self.request.GET.get('user_id')
            if user_id:
                form.instance.user = User.objects.get(id=user_id)
            else:
                messages.error(self.request, "Erro: Nenhum usuário selecionado para associação.")
                return self.form_invalid(form)

        self.object = form.save()
        messages.success(self.request, "Associado atualizado com sucesso!")

        # Redireciona com base no botão clicado
        if "save_and_continue" in self.request.POST:
            return redirect(reverse('app_associados:edit_associado', kwargs={'pk': self.object.pk}))
        elif "save_and_view" in self.request.POST:
            return redirect(reverse('app_associados:single_associado', kwargs={'pk': self.object.pk}))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('app_associados:single_associado', kwargs={'pk': self.object.pk})


# ================================ #
# # Lista Por Associação View
class ListAssociadosAssociacaoView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = AssociadoModel
    template_name = 'app_associados/list_por_associacao.html'
    context_object_name = 'associados'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        ]
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # Filtra associados com base no tipo de usuário logado
        if user.groups.filter(name='Admin da Associação').exists():
            try:
                administrador = IntegrantesModel.objects.get(user=user)
                queryset = queryset.filter(associacao=administrador.associacao)
            except IntegrantesModel.DoesNotExist:
                return queryset.none()
        elif user.groups.filter(name='Delegado da Repartição').exists():
            try:
                delegado = IntegrantesModel.objects.get(user=user)
                queryset = queryset.filter(reparticao=delegado.reparticao)
            except IntegrantesModel.DoesNotExist:
                return queryset.none()

        # Aplica filtros da request (associação, repartição, status)
        associacao_id = self.request.GET.get('associacao')
        reparticao_id = self.request.GET.get('reparticao')
        status = self.request.GET.get('status')

        if associacao_id:
            queryset = queryset.filter(associacao_id=associacao_id)
        if reparticao_id:
            queryset = queryset.filter(reparticao_id=reparticao_id)
        if status:
            queryset = queryset.filter(status=status)

        # Filtro de busca (q)
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(cpf__icontains=query)
            )

        return queryset.order_by('user__first_name', 'user__last_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Adiciona associações e repartições ao contexto
        if user.groups.filter(name='Admin da Associação').exists():
            try:
                administrador = IntegrantesModel.objects.get(user=user)
                context['associacoes'] = AssociacaoModel.objects.filter(id=administrador.associacao_id)
                context['reparticoes'] = ReparticoesModel.objects.filter(associacao_id=administrador.associacao_id)
            except IntegrantesModel.DoesNotExist:
                context['associacoes'] = AssociacaoModel.objects.none()
                context['reparticoes'] = ReparticoesModel.objects.none()
        elif user.groups.filter(name='Delegado da Repartição').exists():
            try:
                delegado = IntegrantesModel.objects.get(user=user)
                context['associacoes'] = AssociacaoModel.objects.filter(reparticoes__id=delegado.reparticao_id)
                context['reparticoes'] = ReparticoesModel.objects.filter(id=delegado.reparticao_id)
            except IntegrantesModel.DoesNotExist:
                context['associacoes'] = AssociacaoModel.objects.none()
                context['reparticoes'] = ReparticoesModel.objects.none()
        else:
            context['associacoes'] = AssociacaoModel.objects.all()
            context['reparticoes'] = ReparticoesModel.objects.all()

        context['status_choices'] = STATUS_CHOICES

        # Passa os valores selecionados para o template
        context['selected_associacao'] = self.request.GET.get('associacao', '')
        context['selected_reparticao'] = self.request.GET.get('reparticao', '')
        context['selected_status'] = self.request.GET.get('status', '')

        return context


# Lista de Associados por Repartição View
class ListAssociadosReparticaoView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = AssociadoModel
    template_name = 'app_associados/list_por_reparticao.html'
    context_object_name = 'associados'
    group_required = ['Delegado(a) da Repartição']

    def get_queryset(self):
        user = self.request.user

        # Inicia o queryset vazio
        queryset = AssociadoModel.objects.none()

        # Filtra os associados pela repartição do delegado logado
        if user.groups.filter(name='Delegado(a) da Repartição').exists():
            try:
                delegado = IntegrantesModel.objects.get(user=user)
                queryset = AssociadoModel.objects.filter(reparticao=delegado.reparticao)
            except IntegrantesModel.DoesNotExist:
                pass

        # Filtros opcionais
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)

        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(cpf__icontains=query)
            )

        return queryset.order_by('user__first_name', 'user__last_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Adiciona informações da associação e repartição ao contexto
        if user.groups.filter(name='Delegado(a) da Repartição').exists():
            try:
                delegado = IntegrantesModel.objects.get(user=user)
                reparticao = delegado.reparticao
                context['associacao'] = reparticao.associacao
                context['reparticao'] = reparticao
            except IntegrantesModel.DoesNotExist:
                context['associacao'] = None
                context['reparticao'] = None
        else:
            context['associacao'] = None
            context['reparticao'] = None

        # Adiciona filtros ao contexto
        context['status_choices'] = STATUS_CHOICES
        context['selected_status'] = self.request.GET.get('status', '')

        return context


class CreateProfissaoView(CreateView):
    model = ProfissoesModel
    form_class = ProfissaoForm
    template_name = 'app_associados/create_profissao.html'
    success_url = reverse_lazy('app_associados:create_profissao')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Listar profissões em ordem alfabética
        context['profissoes'] = ProfissoesModel.objects.all().order_by('nome')
        return context

# View para editar profissão
class EditProfissaoView(UpdateView):
    model = ProfissoesModel
    form_class = ProfissaoForm
    template_name = 'app_associados/edit_profissao.html'
    success_url = reverse_lazy('app_associados:create_profissao')
    

def filtro_reparticoes(request, associacao_id):
    print(f"Associação ID recebido: {associacao_id}")  # Log para depuração
    reparticoes = ReparticoesModel.objects.filter(associacao_id=associacao_id).values('id', 'nome_reparticao')
    print(f"Repartições encontradas: {list(reparticoes)}")  # Log para depuração
    return JsonResponse({'reparticoes': list(reparticoes)})

def filtro_municipios(request, reparticao_id):
    print(f"Repartição ID recebido: {reparticao_id}")  # Log para depuração
    reparticao = get_object_or_404(ReparticoesModel, id=reparticao_id)
    municipios = reparticao.municipios_circunscricao.all().values('id', 'municipio')

    print(f"Municípios encontrados: {list(municipios)}")  # Log para depuração
    return JsonResponse({'municipios': list(municipios)})