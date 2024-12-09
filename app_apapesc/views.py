from django.urls import reverse
from django.shortcuts import redirect, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib import messages
from django.utils.timezone import now

from .models import (
    ApapescModel,
    ReparticoesModel,
    IntegrantesModel,
    MunicipiosModel,
    CargosModel
    )


User = get_user_model()

class UserListView(ListView):
    model = User
    template_name = 'app_apapesc/list_users.html'
    context_object_name = 'users'
    paginate_by = 10  # Número de resultados por página

    def get_queryset(self):
        queryset = super().get_queryset()
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
        # Obter os IDs dos usuários que já são integrantes e os que estão desligados
        integrantes = IntegrantesModel.objects.all()
        context['integrantes_ativos_ids'] = set(
            integrantes.filter(data_saida__isnull=True).values_list('user_id', flat=True)
        )
        context['integrantes_desligados_ids'] = set(
            integrantes.filter(data_saida__isnull=False).values_list('user_id', flat=True)
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
        return redirect(reverse('app_apapesc:edit_integrante', args=[integrante.id]))
    except IntegrantesModel.DoesNotExist:
        messages.error(request, "Usuário não encontrado como integrante.")
    return redirect(reverse('app_apapesc:list_users'))



# Views Cargos
class CargoscListView(ListView):
    model = CargosModel
    template_name = 'app_apapesc/list_cargos.html'
    context_object_name = 'cargos_list'



# Views Apapesc
class ApapescListView(ListView):
    model = ApapescModel
    template_name = 'app_apapesc/list_apapesc.html'
    context_object_name = 'apapesc_list'

class ApapescDetailView(DetailView):
    model = ApapescModel
    template_name = 'app_apapesc/single_apapesc.html'
    context_object_name = 'apapesc'

class ApapescCreateView(CreateView):
    model = ApapescModel
    template_name = 'app_apapesc/create_apapesc.html'
    fields = '__all__'
    success_url = reverse_lazy('app_apapesc:list_apapesc')

class ApapescUpdateView(UpdateView):
    model = ApapescModel
    template_name = 'app_apapesc/edit_apapesc.html'
    fields = '__all__'
    success_url = reverse_lazy('app_apapesc:list_apapesc')

class ApapescDeleteView(DeleteView):
    model = ApapescModel
    template_name = 'app_apapesc/delete_apapesc.html'
    success_url = reverse_lazy('app_apapesc:list_apapesc')



# Views integrantes
class IntegrantesListView(ListView):
    model = IntegrantesModel
    template_name = 'app_apapesc/list_integrante.html'
    context_object_name = 'integrantes_list'

    def get_queryset(self):
        # Retorna apenas integrantes ativos (sem data de saída)
        return IntegrantesModel.objects.filter(data_saida__isnull=True)


class IntegrantesDetailView(DetailView):
    model = IntegrantesModel
    template_name = 'app_apapesc/single_integrante.html'
    context_object_name = 'integrante'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        integrante = self.get_object()

        # Obter informações relacionadas
        context['reparticao'] = integrante.reparticao
        context['apapesc'] = integrante.reparticao.apapesc if integrante.reparticao else None
        context['delegado'] = integrante.reparticao.delegado if integrante.reparticao else None

        return context

class IntegrantesCreateView(CreateView):
    model = IntegrantesModel
    template_name = 'app_apapesc/create_integrante.html'
    fields = '__all__'
    success_url = reverse_lazy('app_apapesc:list_integrante')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.GET.get('user_id')  # Obtém o ID do usuário da URL
        if user_id:
            context['user'] = User.objects.get(id=user_id)
        return context

    def form_valid(self, form):
        form.instance.user = User.objects.get(id=self.request.POST.get('user'))
        return super().form_valid(form)

class IntegrantesUpdateView(UpdateView):
    model = IntegrantesModel
    template_name = 'app_apapesc/edit_integrante.html'
    fields = '__all__'
    success_url = reverse_lazy('app_apapesc:list_integrante')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obter o usuário relacionado ao integrante
        context['user'] = self.object.user  # self.object é o IntegrantesModel sendo editado
        return context
    
class IntegrantesDeleteView(ListView):
    model = IntegrantesModel
    template_name = 'app_apapesc/delete_integrante.html'
    success_url = reverse_lazy('app_apapesc:list_integrante')


class ExIntegrantesListView(ListView):
    model = IntegrantesModel
    template_name = 'app_apapesc/zex_integrantes.html'
    context_object_name = 'ex_integrantes'

    def get_queryset(self):
        # Retorna apenas ex-integrantes (com data de saída preenchida)
        return IntegrantesModel.objects.filter(data_saida__isnull=False)



# Views Municipios
class MunicipiosListView(ListView):
    model = MunicipiosModel
    template_name = 'app_apapesc/list_municipio.html'
    context_object_name = 'municipios_list'

class MunicipiosDetailView(DetailView):
    model = MunicipiosModel
    template_name = 'app_apapesc/single_municipio.html'
    context_object_name = 'municipio'

class MunicipiosCreateView(CreateView):
    model = MunicipiosModel
    template_name = 'app_apapesc/create_municipio.html'
    fields = '__all__'
    success_url = reverse_lazy('app_apapesc:list_municipio')
    

class MunicipiosUpdateView(UpdateView):
    model = MunicipiosModel
    template_name = 'app_apapesc/edit_municipio.html'
    fields = '__all__'
    success_url = reverse_lazy('app_apapesc:list_municipio')

class MunicipiosDeleteView(DeleteView):
    model = MunicipiosModel
    template_name = 'app_apapesc/delete_municipio.html'
    success_url = reverse_lazy('app_apapesc:list_municipio')



# Views Repartições
class ReparticoesListView(ListView):
    model = ReparticoesModel
    template_name = 'app_apapesc/list_reparticao.html'
    context_object_name = 'reparticoes_list'

class ReparticoesDetailView(DetailView):
    model = ReparticoesModel
    template_name = 'app_apapesc/single_reparticao.html'
    context_object_name = 'reparticao'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['municipios_circunscricao'] = self.object.municipios_circunscricao.all()
        return context

class ReparticoesCreateView(CreateView):
    model = ReparticoesModel
    template_name = 'app_apapesc/create_reparticao.html'
    fields = '__all__'
    success_url = reverse_lazy('app_apapesc:list_reparticao')
    
    def form_valid(self, form):
        self.object = form.save()

        if "save_and_continue" in self.request.POST:
            return redirect('app_apapesc:edit_reparticao', pk=self.object.pk)

        if "save_and_view" in self.request.POST:
            return redirect('app_apapesc:single_reparticao', pk=self.object.pk)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('app_associados:detalhe_associado', kwargs={'pk': self.object.pk})    

class ReparticoesUpdateView(UpdateView):
    model = ReparticoesModel
    template_name = 'app_apapesc/edit_reparticao.html'
    fields = '__all__'
    success_url = reverse_lazy('app_apapesc:list_reparticao')

    def form_valid(self, form):
        self.object = form.save()

        if "save_and_continue" in self.request.POST:
            return redirect('app_apapesc:edit_reparticao', pk=self.object.pk)

        if "save_and_view" in self.request.POST:
            return redirect('app_apapesc:single_reparticao', pk=self.object.pk)

        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context
    
class ReparticoesDeleteView(DeleteView):
    model = ReparticoesModel
    template_name = 'app_apapesc/delete_reparticao.html'
    success_url = reverse_lazy('app_apapesc:list_reparticao')
