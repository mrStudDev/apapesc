# app_embarcacoes/views.py

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import EmbarcacoesModel
from .forms import EmbarcacaoForm
from app_associados.models import AssociadoModel
from django.contrib import messages
from app_licencas.models import LicencasModel  # Adjust the import path as needed
from datetime import date, timedelta

class CreateEmbarcacaoView(LoginRequiredMixin, CreateView):
    model = EmbarcacoesModel
    form_class = EmbarcacaoForm
    template_name = 'app_embarcacoes/create_embarcacao.html'

    def dispatch(self, request, *args, **kwargs):
        self.associado = get_object_or_404(AssociadoModel, id=kwargs.get('associado_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['proprietario'] = self.associado
        return kwargs

    def form_valid(self, form):
        embarcacao = form.save(commit=False)
        embarcacao.proprietario = self.associado
        embarcacao.save()

        messages.success(self.request, "Embarcação criada com sucesso! 🚤")
        return redirect('app_embarcacoes:list_embarcacoes')

    def form_invalid(self, form):
        messages.error(self.request, "Erro ao salvar embarcação. Verifique os campos obrigatórios.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Nova Embarcação"
        context['associado'] = self.associado
        return context
    

class ListEmbarcacoesView(LoginRequiredMixin, ListView):
    model = EmbarcacoesModel
    template_name = 'app_embarcacoes/list_embarcacoes.html'
    context_object_name = 'embarcacoes'

    def get_queryset(self):
        return EmbarcacoesModel.objects.select_related('proprietario__user').prefetch_related('licencas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Lista Geral de Embarcações"
        return context

        return context


class SingleEmbarcacaoView(LoginRequiredMixin, DetailView):
    model = EmbarcacoesModel
    template_name = 'app_embarcacoes/single_embarcacao.html'
    context_object_name = 'embarcacao'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        embarcacao = self.get_object()
        context['titulo'] = "Detalhes da Embarcação"
        context['licencas'] = embarcacao.licencas.order_by('-validade_final')
        return context
   
    
    
class EditEmbarcacaoView(UpdateView):
    model = EmbarcacoesModel
    form_class = EmbarcacaoForm
    template_name = 'app_embarcacoes/edit_embarcacao.html'
    context_object_name = 'embarcacao'

    def get_success_url(self):
        messages.success(self.request, "Embarcação atualizada com sucesso! ⚓")
        return reverse('app_embarcacoes:single_embarcacao', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Embarcação"
        return context