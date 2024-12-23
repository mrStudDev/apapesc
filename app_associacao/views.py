from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth.models import User
from app_associados.models import AssociadoModel
from app_associacao.forms import IntegranteForm
from accounts.mixins import GroupPermissionRequiredMixin 
from django.contrib.auth.models import Group
from app_documentos.models import Documento
from django.http import Http404

from .models import (
    AssociacaoModel,
    ReparticoesModel,
    IntegrantesModel,
    MunicipiosModel,
    CargosModel
    )


User = get_user_model()


class UserListView(ListView):
    model = User
    template_name = 'app_associacao/list_users.html'
    context_object_name = 'users'
    paginate_by = 20


    def get_queryset(self):
        queryset = super().get_queryset().order_by('first_name', 'last_name')
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # IDs dos usuários que já são integrantes
        integrantes = IntegrantesModel.objects.all()
        context['integrantes_ativos_ids'] = set(
            integrantes.filter(data_saida__isnull=True).values_list('user_id', flat=True)
        )
        context['integrantes_desligados_ids'] = set(
            integrantes.filter(data_saida__isnull=False).values_list('user_id', flat=True)
        )

        # IDs dos usuários que já são associados
        associados = AssociadoModel.objects.all()
        context['associados_ids'] = set(
            associados.values_list('user_id', flat=True)
        )

        return context


def reintegrate_integrante(request):
    user_id = request.GET.get('user_id')
    try:
        integrante = IntegrantesModel.objects.get(user_id=user_id)
        integrante.data_saida = None  # Limpa a data de saída
        integrante.data_entrada = now().date()  # Define a data de reintegração
        integrante.save()

        messages.success(request, "Usuário reintegrado com sucesso!")
        # Redireciona para a página de edição do integrante
        return redirect(reverse('app_associacao:edit_integrante', args=[integrante.id]))
    except IntegrantesModel.DoesNotExist:
        messages.error(request, "Usuário não encontrado como integrante.")
    return redirect(reverse('app_associacao:list_users'))



# Views Cargos
class CargoscListView(GroupPermissionRequiredMixin, ListView):
    model = CargosModel
    template_name = 'app_associacao/list_cargo.html'
    context_object_name = 'cargos_list'
    group_required = ['Superuser', 'Admin da Associação']

class CargoDetailView(GroupPermissionRequiredMixin, DeleteView):
    model = CargosModel
    template_name = 'app_associacao/single_cargo.html'
    context_object_name = 'cargo'
    group_required = ['Superuser', 'Admin da Associação']

class CargoCreateView(GroupPermissionRequiredMixin, CreateView):
    model = CargosModel
    template_name = 'app_associacao/create_cargo.html'
    fields = '__all__'
    success_url = reverse_lazy('app_associacao:list_cargo')    
    group_required = ['Superuser', 'Admin da Associação']
    

class CargoUpdateView(GroupPermissionRequiredMixin, UpdateView):
    model = CargosModel
    template_name = 'app_associacao/edit_cargo.html'
    fields = '__all__'
    success_url = reverse_lazy('app_associacao:list_cargos')
    group_required = ['Superuser', 'Admin da Associação']
    

class CargoDeleteView(GroupPermissionRequiredMixin, DeleteView):
    model = CargosModel
    template_name = 'app_associacao/delete_cargo.html'
    success_url = reverse_lazy('app_associacao:list_cargo')
    group_required = ['Superuser', 'Admin da Associação']
    

# Views Associação
class AssociacaoListView(GroupPermissionRequiredMixin, ListView):
    model = AssociacaoModel
    template_name = 'app_associacao/list_associacao.html'
    context_object_name = 'associacao_list'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]


class AssociacaoDetailView(GroupPermissionRequiredMixin, DetailView):
    model = AssociacaoModel
    template_name = 'app_associacao/single_associacao.html'
    context_object_name = 'associacao'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        associacao = self.get_object()
        context['documentos'] = Documento.objects.filter(associacao=associacao)
        return context
    

class AssociacaoCreateView(GroupPermissionRequiredMixin, CreateView):
    model = AssociacaoModel
    template_name = 'app_associacao/create_associacao.html'
    fields = '__all__'
    success_url = reverse_lazy('app_associacao:list_associacao')
    group_required = ['Superuser',]
    
class AssociacaoUpdateView(GroupPermissionRequiredMixin, UpdateView):
    model = AssociacaoModel
    template_name = 'app_associacao/edit_associacao.html'
    fields = '__all__'
    success_url = reverse_lazy('app_associacao:list_associacao')
    group_required = ['Superuser',]    

class AssociacaoDeleteView(GroupPermissionRequiredMixin, DeleteView):
    model = AssociacaoModel
    template_name = 'app_associacao/delete_associacao.html'
    success_url = reverse_lazy('app_associacao:list_associacao')
    group_required = ['Superuser',]

# Views integrantes
class IntegrantesListView(GroupPermissionRequiredMixin, ListView):
    model = IntegrantesModel
    template_name = 'app_associacao/list_integrante.html'
    context_object_name = 'integrantes_list'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]
    
    def get_queryset(self):
        
        # Retorna apenas integrantes ativos (sem data de saída)
        return IntegrantesModel.objects.filter(
            data_saida__isnull=True).order_by('user__first_name', 'user__last_name')


class IntegrantesDetailView(GroupPermissionRequiredMixin, DetailView):
    model = IntegrantesModel
    template_name = 'app_associacao/single_integrante.html'
    context_object_name = 'integrante'
    group_required = [
        'Superuser',
        'Admin da Associação',
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        integrante = self.get_object()

        # Obter informações relacionadas
        context['reparticao'] = integrante.reparticao
        context['associacao'] = integrante.reparticao.associacao if integrante.reparticao else None
        context['delegado'] = integrante.reparticao.delegado if integrante.reparticao else None
        context['documentos'] = Documento.objects.filter(integrante=integrante)
        return context


class IntegrantesCreateView(GroupPermissionRequiredMixin, CreateView):
    model = IntegrantesModel
    form_class = IntegranteForm
    template_name = 'app_associacao/create_integrante.html'
    success_url = reverse_lazy('app_associacao:list_integrante')
    group_required = [
        'Superuser',
        'Admin da Associação',
        # Inclua outros grupos se necessário
    ]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user_id = self.request.GET.get('user_id')
        if user_id:
            try:
                kwargs['user'] = User.objects.get(id=user_id)
            except User.DoesNotExist:
                messages.error(self.request, "Usuário não encontrado.")
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.GET.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                context['user'] = user
            except User.DoesNotExist:
                context['user'] = None
                messages.error(self.request, "Usuário não encontrado.")

        if self.request.method == "POST":
            context['form'] = self.form_class(self.request.POST)
        else:
            context['form'] = self.get_form()

        return context

    def form_valid(self, form):
        user_id = self.request.GET.get('user_id')
        if not user_id:
            messages.error(self.request, "Erro: Nenhum usuário selecionado para integrar.")
            return self.form_invalid(form)

        try:
            user = User.objects.get(id=user_id)
            form.instance.user = user  # Associa o User ao IntegrantesModel
        except User.DoesNotExist:
            messages.error(self.request, "Usuário não encontrado.")
            return self.form_invalid(form)

        # Remove qualquer lógica que altere o email do User.
        # Salva apenas o modelo de integrantes.
        self.object = form.save()
        messages.success(self.request, "Integrante criado com sucesso!")

        # Se quiser tratar botões diferentes ("save_and_continue", etc.)
        if "save_and_continue" in self.request.POST:
            return redirect(reverse('app_associacao:edit_integrante', kwargs={'pk': self.object.pk}))
        elif "save_and_view" in self.request.POST:
            return redirect(reverse('app_associacao:single_integrante', kwargs={'pk': self.object.pk}))

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('app_associacao:list_integrante')




class IntegrantesUpdateView(GroupPermissionRequiredMixin, UpdateView):
    model = IntegrantesModel
    template_name = 'app_associacao/edit_integrante.html'
    form_class = IntegranteForm
    success_url = reverse_lazy('app_associacao:list_integrante')
    group_required = [
        'Superuser',
        'Admin da Associação',
    ]

    def get_initial(self):
        initial = super().get_initial()
        # Preenche o campo 'group' com o grupo do usuário relacionado
        user_groups = self.object.user.groups.all()
        if user_groups.exists():
            initial['group'] = user_groups.first()  # Assume que o usuário está em apenas um grupo
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obter o usuário relacionado ao integrante
        context['user'] = self.object.user  # self.object é o IntegrantesModel sendo editado
        return context

    def form_valid(self, form):
        # Atualiza os grupos do usuário conforme o selecionado
        group = form.cleaned_data.get('group')
        if group:
            self.object.user.groups.clear()  # Remove todos os grupos existentes
            self.object.user.groups.add(group)  # Adiciona o grupo selecionado
        return super().form_valid(form)

    
    
class IntegrantesDeleteView(GroupPermissionRequiredMixin, ListView):
    model = IntegrantesModel
    template_name = 'app_associacao/delete_integrante.html'
    success_url = reverse_lazy('app_associacao:list_integrante')
    group_required = [
        'Superuser',
        'Admin da Associação',
        ]

class ExIntegrantesListView(GroupPermissionRequiredMixin, ListView):
    model = IntegrantesModel
    template_name = 'app_associacao/zex_integrantes.html'
    context_object_name = 'ex_integrantes'
    group_required = [
        'Superuser',
        'Admin da Associação',
        ]
    
    def get_queryset(self):
        # Retorna apenas ex-integrantes (com data de saída preenchida)
        return IntegrantesModel.objects.filter(data_saida__isnull=False)



# Views Municipios
class MunicipiosListView(GroupPermissionRequiredMixin, ListView):
    model = MunicipiosModel
    template_name = 'app_associacao/list_municipio.html'
    context_object_name = 'municipios_list'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]    

class MunicipiosDetailView(GroupPermissionRequiredMixin, DetailView):
    model = MunicipiosModel
    template_name = 'app_associacao/single_municipio.html'
    context_object_name = 'municipio'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]    

class MunicipiosCreateView(GroupPermissionRequiredMixin, CreateView):
    model = MunicipiosModel
    template_name = 'app_associacao/create_municipio.html'
    fields = '__all__'
    success_url = reverse_lazy('app_associacao:list_municipio')
    group_required = [
        'Superuser',
        'Admin da Associação',
        ]    

class MunicipiosUpdateView(GroupPermissionRequiredMixin, UpdateView):
    model = MunicipiosModel
    template_name = 'app_associacao/edit_municipio.html'
    fields = '__all__'
    success_url = reverse_lazy('app_associacao:list_municipio')
    group_required = [
        'Superuser',
        'Admin da Associação',
        ]
    
class MunicipiosDeleteView(GroupPermissionRequiredMixin, DeleteView):
    model = MunicipiosModel
    template_name = 'app_associacao/delete_municipio.html'
    success_url = reverse_lazy('app_associacao:list_municipio')
    group_required = [
        'Superuser',
        'Admin da Associação',
        ]


# Views Repartições
class ReparticoesListView(GroupPermissionRequiredMixin, ListView):
    model = ReparticoesModel
    template_name = 'app_associacao/list_reparticao.html'
    context_object_name = 'reparticoes_list'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]    

class ReparticoesDetailView(GroupPermissionRequiredMixin, DetailView):
    model = ReparticoesModel
    template_name = 'app_associacao/single_reparticao.html'
    context_object_name = 'reparticao'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['municipios_circunscricao'] = self.object.municipios_circunscricao.all()
        context['documentos'] = Documento.objects.filter(reparticao=self.object)
        return context

class ReparticoesCreateView(GroupPermissionRequiredMixin, CreateView):
    model = ReparticoesModel
    template_name = 'app_associacao/create_reparticao.html'
    fields = '__all__'
    success_url = reverse_lazy('app_associacao:list_reparticao')
    group_required = [
        'Superuser',
        'Admin da Associação',
        ]    
    
    def form_valid(self, form):
        self.object = form.save()

        if "save_and_continue" in self.request.POST:
            return redirect('app_associacao:edit_reparticao', pk=self.object.pk)

        if "save_and_view" in self.request.POST:
            return redirect('app_associacao:single_reparticao', pk=self.object.pk)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('app_associados:detalhe_associado', kwargs={'pk': self.object.pk})    

class ReparticoesUpdateView(GroupPermissionRequiredMixin, UpdateView):
    model = ReparticoesModel
    template_name = 'app_associacao/edit_reparticao.html'
    fields = '__all__'
    success_url = reverse_lazy('app_associacao:list_reparticao')
    group_required = [
        'Superuser',
        'Admin da Associação',
        ]
    
    def form_valid(self, form):
        self.object = form.save()

        if "save_and_continue" in self.request.POST:
            return redirect('app_associacao:edit_reparticao', pk=self.object.pk)

        if "save_and_view" in self.request.POST:
            return redirect('app_associacao:single_reparticao', pk=self.object.pk)

        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context
    
class ReparticoesDeleteView(GroupPermissionRequiredMixin, DeleteView):
    model = ReparticoesModel
    template_name = 'app_associacao/delete_reparticao.html'
    success_url = reverse_lazy('app_associacao:list_reparticao')
    group_required = [
        'Superuser',
        'Admin da Associação',
        ]