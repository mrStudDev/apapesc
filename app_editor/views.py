# App Editor
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from .models import NotasApapescModel
from .forms import NotaForm

# Listagem de notas
class NotasListView(ListView):
    model = NotasApapescModel
    template_name = 'app_editor/list_notas.html'
    context_object_name = 'notas'

class NotaCreateView(CreateView):
    model = NotasApapescModel
    form_class = NotaForm  # Aqui vinculamos o formulário
    template_name = 'app_editor/create_nota.html'
    success_url = reverse_lazy('app_editor:list_notas') 