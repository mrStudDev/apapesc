# app_licencas/views.py
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, UpdateView, ListView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from app_embarcacoes.models import EmbarcacoesModel
from .models import LicencasModel
from .forms import LicencaForm
from datetime import date, timedelta
from accounts.mixins import GroupPermissionRequiredMixin 
from django.contrib.auth.mixins import LoginRequiredMixin


class CreateLicencaView(LoginRequiredMixin, GroupPermissionRequiredMixin, CreateView):
    model = LicencasModel
    form_class = LicencaForm
    template_name = 'app_licencas/create_licenca.html'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        'Associados da Associação',
    ]


    def dispatch(self, request, *args, **kwargs):
        self.embarcacao = get_object_or_404(EmbarcacoesModel, id=kwargs.get('embarcacao_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['embarcacao'] = self.embarcacao  # para uso no form, se necessário
        return kwargs

    def form_valid(self, form):
        licenca = form.save(commit=False)
        licenca.embarcacao = self.embarcacao
        licenca.save()
        messages.success(self.request, "Licença cadastrada com sucesso! 📄")
        self.object = licenca  # ⬅️ necessário para usar self.object em get_success_url
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('app_licencas:single_licenca', kwargs={'pk': self.object.pk})


    def form_invalid(self, form):
        messages.error(self.request, "Erro ao salvar a licença. Verifique os campos obrigatórios.")
        return super().form_invalid(form)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Nova Licença"
        context['embarcacao'] = self.embarcacao
        context['associado'] = self.embarcacao.proprietario
        return context


class SingleLicencaView(LoginRequiredMixin, GroupPermissionRequiredMixin, DetailView):
    model = LicencasModel
    template_name = 'app_licencas/single_licenca.html'
    context_object_name = 'licenca'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Delegado(a) da Repartição',
        'Diretor(a) da Associação',
        'Presidente da Associação',
        'Auxiliar da Associação',
        'Auxiliar da Repartição',
        'Associados da Associação',
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        licenca = self.get_object()
        context['embarcacao'] = licenca.embarcacao
        context['associado'] = licenca.embarcacao.proprietario
        context['titulo'] = "Detalhes da Licença"
        return context



class EditLicencaView(LoginRequiredMixin, GroupPermissionRequiredMixin, UpdateView):
    model = LicencasModel
    form_class = LicencaForm
    template_name = 'app_licencas/edit_licenca.html'
    context_object_name = 'licenca'
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
        messages.success(self.request, "Licença atualizada com sucesso! ✅")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erro ao atualizar a licença. Verifique os campos obrigatórios.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('app_licencas:single_licenca', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Licença"
        context['embarcacao'] = self.object.embarcacao
        context['associado'] = self.object.embarcacao.proprietario
        return context    

from django.db.models import Q, Value
from django.db.models.functions import Concat

class ListLicencasView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = LicencasModel
    template_name = 'app_licencas/list_licencas.html'
    context_object_name = 'licencas'
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
        queryset = LicencasModel.objects.select_related(
            'embarcacao__proprietario__user'
        ).order_by('-validade_final')

        nome_embarcacao = self.request.GET.get('embarcacao', '').strip()
        nome_associado = self.request.GET.get('associado', '').strip()

        # Filtro por nome da embarcação
        if nome_embarcacao:
            queryset = queryset.filter(
                embarcacao__nome_embarcacao__icontains=nome_embarcacao
            )

        # Filtro por nome do associado
        if nome_associado:
            queryset = queryset.filter(
                Q(embarcacao__proprietario__user__first_name__icontains=nome_associado) |
                Q(embarcacao__proprietario__user__last_name__icontains=nome_associado) |
                Q(embarcacao__proprietario__user__username__icontains=nome_associado) |
                Q(embarcacao__proprietario__user__email__icontains=nome_associado)
            )
                  

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nome_embarcacao'] = self.request.GET.get('embarcacao', '')
        context['nome_associado'] = self.request.GET.get('associado', '')
        return context



class DeleteLicencaView(LoginRequiredMixin, GroupPermissionRequiredMixin, DeleteView):
    model = LicencasModel
    template_name = 'app_licencas/delete_licenca.html'
    context_object_name = 'licenca'
    success_url = reverse_lazy('app_licencas:list_licencas')
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
        licenca = self.get_object()
        context['titulo'] = "Excluir Licença"
        context['embarcacao'] = licenca.embarcacao
        context['associado'] = licenca.embarcacao.proprietario
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        embarcacao_id = self.object.embarcacao.id
        messages.success(request, "Licença excluída com sucesso! 🗑️")
        self.object.delete()
        return redirect(reverse('app_embarcacoes:single_embarcacao', kwargs={'pk': embarcacao_id}))