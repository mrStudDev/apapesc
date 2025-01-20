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
from app_associacao.forms import IntegranteForm, AssociacaoForm, ReparticaoForm
from accounts.mixins import GroupPermissionRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
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


class UserListView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = User
    template_name = 'app_associacao/list_users.html'
    context_object_name = 'users'
    paginate_by = 20
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
class CargoscListView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = CargosModel
    template_name = 'app_associacao/list_cargo.html'
    context_object_name = 'cargos_list'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]


class CargoDetailView(LoginRequiredMixin, GroupPermissionRequiredMixin, DeleteView):
    model = CargosModel
    template_name = 'app_associacao/single_cargo.html'
    context_object_name = 'cargo'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]

class CargoCreateView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = CargosModel
    template_name = 'app_associacao/create_cargo.html'
    fields = '__all__'
    success_url = reverse_lazy('app_associacao:list_cargo')    
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]
    

class CargoUpdateView(LoginRequiredMixin, GroupPermissionRequiredMixin, UpdateView):
    model = CargosModel
    template_name = 'app_associacao/edit_cargo.html'
    fields = '__all__'
    success_url = reverse_lazy('app_associacao:list_cargos')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]
    

class CargoDeleteView(LoginRequiredMixin, GroupPermissionRequiredMixin, DeleteView):
    model = CargosModel
    template_name = 'app_associacao/delete_cargo.html'
    success_url = reverse_lazy('app_associacao:list_cargo')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]
    

# Views Associação -
class AssociacaoListView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = AssociacaoModel
    template_name = 'app_associacao/list_associacao.html'
    context_object_name = 'associacao_list'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]


class AssociacaoDetailView(LoginRequiredMixin, GroupPermissionRequiredMixin, DetailView):
    model = AssociacaoModel
    template_name = 'app_associacao/single_associacao.html'
    context_object_name = 'associacao'
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
        associacao = self.get_object()
        context['documentos'] = Documento.objects.filter(associacao=associacao)
        return context
    

class AssociacaoCreateView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = AssociacaoModel
    template_name = 'app_associacao/create_associacao.html'
    form_class = AssociacaoForm
    success_url = reverse_lazy('app_associacao:list_associacao')
    group_required = [
        'Superuser',
        'Admin da Associação',
        ]

    def form_valid(self, form):
        # Deixe o Django cuidar do salvamento do ManyToMany
        response = super().form_valid(form)
        # Aqui, `self.object` já foi salvo e o M2M (diretores) também
        messages.success(self.request, "Associação salva com sucesso!")

        # Lógica de redirecionamento
        if "save_and_continue" in self.request.POST:
            messages.info(self.request, "Redirecionando para edição da associação.")
            return redirect('app_associacao:edit_associacao', pk=self.object.pk)

        if "save_and_view" in self.request.POST:
            messages.info(self.request, "Redirecionando para visualização da associação.")
            return redirect('app_associacao:single_associacao', pk=self.object.pk)
        
        # Se nenhum botão especial foi clicado, retorna o fluxo normal
        return response

    
    def get_success_url(self):
        return reverse_lazy('app_associacao:single_associacao', kwargs={'pk': self.object.pk})  
    
class AssociacaoUpdateView(LoginRequiredMixin, GroupPermissionRequiredMixin, UpdateView):
    model = AssociacaoModel
    template_name = 'app_associacao/edit_associacao.html'
    form_class = AssociacaoForm
    success_url = reverse_lazy('app_associacao:list_associacao')
    group_required = [
        'Superuser',
        'Admin da Associação',
        ]

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Associação atualizada com sucesso!")
        return response
    
    def get_success_url(self):
        return reverse_lazy('app_associacao:single_associacao', kwargs={'pk': self.object.pk})  
    
class AssociacaoDeleteView(LoginRequiredMixin, GroupPermissionRequiredMixin, DeleteView):
    model = AssociacaoModel
    template_name = 'app_associacao/delete_associacao.html'
    success_url = reverse_lazy('app_associacao:list_associacao')
    group_required = [
        'Superuser',
        'Admin da Associação',
        ]

# Views integrantes
class IntegrantesListView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = IntegrantesModel
    template_name = 'app_associacao/list_integrante.html'
    context_object_name = 'integrantes_list'
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

        # Se o usuário for superuser, retorna todos os integrantes
        if user.is_superuser:
            return IntegrantesModel.objects.filter(data_saida__isnull=True).order_by('user__first_name', 'user__last_name')

        try:
            # Recupera o integrante correspondente ao usuário logado
            integrante = IntegrantesModel.objects.get(user=user)

            # Filtra integrantes da mesma associação do usuário logado
            return IntegrantesModel.objects.filter(
                associacao=integrante.associacao,
                data_saida__isnull=True
            ).order_by('user__first_name', 'user__last_name')

        except IntegrantesModel.DoesNotExist:
            return IntegrantesModel.objects.none()



class IntegrantesDetailView(LoginRequiredMixin, GroupPermissionRequiredMixin, DetailView):
    model = IntegrantesModel
    template_name = 'app_associacao/single_integrante.html'
    context_object_name = 'integrante'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
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


class IntegrantesCreateView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = IntegrantesModel
    form_class = IntegranteForm
    template_name = 'app_associacao/create_integrante.html'
    success_url = reverse_lazy('app_associacao:list_integrante')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
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
        # Recupera o ID da ASSOCIAÇÂO selecionada
        selected_associacao_id = self.request.GET.get('associacao', '')

        # Adiciona informações dos filtros ao contexto
        context['associacoes'] = AssociacaoModel.objects.all()
        
        # Filtra repartições com base na ASSOCIAÇÂO selecionada
        if selected_associacao_id:
            context['reparticoes'] = ReparticoesModel.objects.filter(associacao_id=selected_associacao_id)
        else:
            context['reparticoes'] = ReparticoesModel.objects.all()

        # Passa os valores selecionados para o template
        context['selected_associacao'] = selected_associacao_id
        context['selected_reparticao'] = self.request.GET.get('reparticao', '')            

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

        self.object = form.save(commit=False)
        
        # Atualiza os grupos do usuário conforme o selecionado
        # Captura o grupo do formulário e associa ao usuário
        group = form.cleaned_data.get('group')
        if group:
            user.groups.clear()  # Remove todos os grupos existentes
            user.groups.add(group) 


        # Remove qualquer lógica que altere o email do User.
        # Salva apenas o modelo de integrantes.
        self.object = form.save()
        messages.success(self.request, "Integrante criado com sucesso!")

        # Se quiser tratar botões diferentes ("save_and_continue", etc.)
        if "save_and_continue" in self.request.POST:
            return redirect(reverse('app_associacao:edit_integrante', kwargs={'pk': self.object.pk}))
        elif "save_and_view" in self.request.POST:
            return redirect(reverse('app_associacao:single_integrante', kwargs={'pk': self.object.pk}))
        
        # Salva o objeto IntegrantesModel no banco de dados
        self.object = form.save()
        messages.success(self.request, "Integrante criado com sucesso!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('app_associacao:list_integrante')


class IntegrantesUpdateView(LoginRequiredMixin, GroupPermissionRequiredMixin, UpdateView):
    model = IntegrantesModel
    template_name = 'app_associacao/edit_integrante.html'
    form_class = IntegranteForm
    success_url = reverse_lazy('app_associacao:list_integrante')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        ]
    
    def get_form_kwargs(self):
        """Adiciona o usuário ao formulário, se necessário."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs
    
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

    
    
class IntegrantesDeleteView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = IntegrantesModel
    template_name = 'app_associacao/delete_integrante.html'
    success_url = reverse_lazy('app_associacao:list_integrante')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        ]

# Ex Integrantes
class ExIntegrantesListView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = IntegrantesModel
    template_name = 'app_associacao/zex_integrantes.html'
    context_object_name = 'ex_integrantes'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
    ]

    def get_queryset(self):
        user = self.request.user

        # Se o usuário for superuser, retorna todos os ex-integrantes
        if user.is_superuser:
            return IntegrantesModel.objects.filter(data_saida__isnull=False).order_by('user__first_name', 'user__last_name')

        try:
            # Recupera o integrante correspondente ao usuário logado
            integrante = IntegrantesModel.objects.get(user=user)

            # Filtra ex-integrantes da mesma associação do usuário logado
            return IntegrantesModel.objects.filter(
                associacao=integrante.associacao,
                data_saida__isnull=False
            ).order_by('user__first_name', 'user__last_name')

        except IntegrantesModel.DoesNotExist:
            return IntegrantesModel.objects.none()




# Views Municipios
class MunicipiosListView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = MunicipiosModel
    template_name = 'app_associacao/list_municipio.html'
    context_object_name = 'municipios_list'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]    

class MunicipiosDetailView(LoginRequiredMixin, GroupPermissionRequiredMixin, DetailView):
    model = MunicipiosModel
    template_name = 'app_associacao/single_municipio.html'
    context_object_name = 'municipio'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]    

class MunicipiosCreateView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = MunicipiosModel
    template_name = 'app_associacao/create_municipio.html'
    fields = '__all__'
    success_url = reverse_lazy('app_associacao:list_municipio')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ]   

class MunicipiosUpdateView(LoginRequiredMixin, GroupPermissionRequiredMixin, UpdateView):
    model = MunicipiosModel
    template_name = 'app_associacao/edit_municipio.html'
    fields = '__all__'
    success_url = reverse_lazy('app_associacao:list_municipio')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ] 
    
class MunicipiosDeleteView(LoginRequiredMixin, GroupPermissionRequiredMixin, DeleteView):
    model = MunicipiosModel
    template_name = 'app_associacao/delete_municipio.html'
    success_url = reverse_lazy('app_associacao:list_municipio')
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        ] 


# Views Repartições
class ReparticoesListView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = ReparticoesModel
    template_name = 'app_associacao/list_reparticao.html'
    context_object_name = 'reparticoes_list'
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

        # Se o usuário for superuser, retorna todas as repartições
        if user.is_superuser:
            return ReparticoesModel.objects.all()

        try:
            # Recupera o integrante correspondente ao usuário logado
            integrante = IntegrantesModel.objects.get(user=user)

            # Grupos que devem ver todas as repartições da associação vinculada
            grupos_associacao = [
                'Admin da Associação',
                'Diretor(a) da Associação',
                'Presidente da Associação',
                'Auxiliar da Associação'
            ]

            # Se o usuário estiver em algum dos grupos que podem ver todas as repartições da associação
            if user.groups.filter(name__in=grupos_associacao).exists():
                return ReparticoesModel.objects.filter(associacao=integrante.associacao)

            # Se o integrante for Delegado(a) da Repartição, retorna apenas a repartição à qual ele está vinculado
            if user.groups.filter(name='Delegado(a) da Repartição').exists():
                return ReparticoesModel.objects.filter(delegado=integrante)

        except IntegrantesModel.DoesNotExist:
            return ReparticoesModel.objects.none()

        # Caso não caia em nenhuma das condições acima, retorna uma queryset vazia
        return ReparticoesModel.objects.none()


class ReparticoesDetailView(LoginRequiredMixin, GroupPermissionRequiredMixin, DetailView):
    model = ReparticoesModel
    template_name = 'app_associacao/single_reparticao.html'
    context_object_name = 'reparticao'
    success_url = reverse_lazy('app_associacao:list_reparticao')
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
        context['municipios_circunscricao'] = self.object.municipios_circunscricao.all()
        context['documentos'] = Documento.objects.filter(reparticao=self.object)
        return context
    
    def get_success_url(self):
        if self.object and self.object.pk:
            return reverse_lazy('app_associacao:single_reparticao', kwargs={'pk': self.object.pk})
        return reverse_lazy('app_associacao:list_reparticao')


class ReparticoesCreateView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = ReparticoesModel
    template_name = 'app_associacao/create_reparticao.html'
    form_class = ReparticaoForm
    success_url = reverse_lazy('app_associacao:list_reparticao')
    group_required = [
        'Superuser',
        'Admin da Associação',
        ]    
    
    def form_valid(self, form):

        response = super().form_valid(form)
        
        messages.success(self.request, "Repartição salva com sucesso!")
        
        if "save_and_continue" in self.request.POST:
            messages.info(self.request, "Redirecionando para edição da Repartição.")
            return redirect('app_associacao:edit_reparticao', pk=self.object.pk)

        if "save_and_view" in self.request.POST:
            messages.info(self.request, "Redirecionando para visualização da Repartição.")
            return redirect('app_associacao:single_reparticao', pk=self.object.pk)

        return response   

    def get_success_url(self):
        return reverse_lazy('app_associacao:single_reparticao', kwargs={'pk': self.object.pk})    
    
   

class ReparticoesUpdateView(LoginRequiredMixin, GroupPermissionRequiredMixin, UpdateView):
    model = ReparticoesModel
    template_name = 'app_associacao/edit_reparticao.html'
    form_class = ReparticaoForm
    success_url = reverse_lazy('app_associacao:list_reparticao')
    group_required = [
        'Superuser',
        'Admin da Associação',
        ]

    def form_valid(self, form):
        response = super().form_valid(form)
        
        messages.success(self.request, "Repartição salva com sucesso!")
        
        if "save_and_continue" in self.request.POST:
            messages.info(self.request, "Redirecionando para edição da Repartição.")
            return redirect('app_associacao:edit_reparticao', pk=self.object.pk)

        if "save_and_view" in self.request.POST:
            messages.info(self.request, "Redirecionando para visualização da Repartição.")
            return redirect('app_associacao:single_reparticao', pk=self.object.pk)

        return response   

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def get_success_url(self):
        if self.object.pk:
            return reverse('app_associacao:single_reparticao', kwargs={'pk': self.object.pk})
        return super().get_success_url()
    
class ReparticoesDeleteView(LoginRequiredMixin, GroupPermissionRequiredMixin, DeleteView):
    model = ReparticoesModel
    template_name = 'app_associacao/delete_reparticao.html'
    success_url = reverse_lazy('app_associacao:list_reparticao')
    group_required = [
        'Superuser',
        'Admin da Associação',
        ]