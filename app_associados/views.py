from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from .models import AssociadoModel
from .forms import AssociadoForm  
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from app_associacao.models import AssociacaoModel, ReparticoesModel, MunicipiosModel, IntegrantesModel
from django.contrib.auth.models import User
from app_associados.models import STATUS_CHOICES
from app_associados.models import AssociadoModel
from accounts.mixins import GroupPermissionRequiredMixin 
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
from django.contrib.auth.models import Group
from app_documentos.models import Documento

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

        # Manipulação do celular_clean
        for associado in context['associados']:
            if associado.celular:
                associado.celular_clean = associado.celular.replace('-', '').replace(' ', '')

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
        context['documentos'] = Documento.objects.filter(associado=associado)
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Passar os dados do associado e configurar campos adicionais
        associado = self.get_object()
        if associado.user:
            context['user'] = associado.user  # Dados do usuário associado

        context['form'].fields['reparticao'].queryset = ReparticoesModel.objects.all()
        context['form'].fields['municipio_circunscricao'].queryset = MunicipiosModel.objects.all()

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
