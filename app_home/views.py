from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib import messages  # Para exibir mensagens de sucesso
from .forms import LeadInformacoesForm  # Importa o formulário
from django.views.generic import ListView, TemplateView, DetailView 
from .models import LeadInformacoes, ContactMessagesModel
from django.shortcuts import get_object_or_404, redirect
from .forms import ContactForm
from accounts.mixins import GroupPermissionRequiredMixin 
from django.contrib.auth.mixins import LoginRequiredMixin

def HomeView(request):
    context = {}

    # Lógica para usuários autenticados
    if request.user.is_authenticated:
        context['is_superuser'] = request.user.is_superuser
        context['is_admin_associacao'] = request.user.groups.filter(name='Admin da Associação').exists()
        context['is_diretor_associacao'] = request.user.groups.filter(name='Diretor(a) da Associação').exists()
        context['is_presidente_associacao'] = request.user.groups.filter(name='Presidente da Associação').exists()
        context['is_delegado_reparticao'] = request.user.groups.filter(name='Delegado(a) da Repartição').exists()
        context['is_auxiliar_associacao'] = request.user.groups.filter(name='Auxiliar da Associação').exists()
        context['is_auxiliar_reparticao'] = request.user.groups.filter(name='Auxiliar da Repartição').exists()
        context['is_associado_associacao'] = request.user.groups.filter(name='Associados da Associação').exists()
        context['is_user_vip'] = request.user.groups.filter(name='User Vip').exists()

    # Processa o formulário de LeadInformacoes
    if request.method == 'POST':
        form = LeadInformacoesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mensagem enviada com sucesso! Entraremos em contato em breve.')
            return redirect('app_home:home')  # Substitua pelo nome correto da sua URL
        else:
            messages.error(request, 'Houve um erro ao enviar sua mensagem. Verifique os dados e tente novamente.')
    else:
        form = LeadInformacoesForm()
 
    # Adiciona o formulário ao contexto
    context['form'] = form

    return render(request, 'app_home/home.html', context)

class SobreNosView(TemplateView):
    template_name = 'app_home/sobre.html'

class ServicosView(TemplateView):
    template_name = 'app_home/servicos.html'
    

class LeadMessagesListView(ListView):
    model = LeadInformacoes
    template_name = 'app_home/list_mensagens.html'
    context_object_name = 'leads'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona a quantidade total de mensagens no contexto
        context['total_leads'] = LeadInformacoes.objects.count()
        return context

def delete_lead_message(request, pk):
    lead = get_object_or_404(LeadInformacoes, pk=pk)
    lead.delete()
    messages.success(request, "Mensagem deletada com sucesso!")
    return redirect('app_home:list_mensagens')


class Associese_View(TemplateView):
    template_name = 'app_home/associe_se.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LeadInformacoesForm()  # Adiciona o formulário ao contexto
        return context

    def post(self, request, *args, **kwargs):
        form = LeadInformacoesForm(request.POST)
        if form.is_valid():
            form.save()  # Salva os dados no banco de dados
            messages.success(request, "Sua mensagem foi enviada com sucesso!")
            return redirect('app_home:associe_se')  # Redireciona para a mesma página após o envio
        else:
            return render(request, self.template_name, {'form': form})



class ListContactMessagesView(LoginRequiredMixin, GroupPermissionRequiredMixin, ListView):
    model = ContactMessagesModel
    template_name = 'app_home/list_contatos.html'
    context_object_name = 'mensagens'
    paginate_by = 10  # Paginação opcional, exibe 10 mensagens por página
    
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Diretor(a) da Associação',
        'Presidente da Associação',
    ]

    def get_queryset(self):
        return ContactMessagesModel.objects.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona a quantidade total de mensagens no contexto
        context['total_mensagens'] = ContactMessagesModel.objects.count()
        return context
    

class ViewContactMessageView(LoginRequiredMixin, GroupPermissionRequiredMixin, DetailView):
    model = ContactMessagesModel
    template_name = 'app_home/single_contato.html'
    context_object_name = 'mensagem'
    group_required = [
        'Superuser',
        'Admin da Associação',
        'Diretor(a) da Associação',
        'Presidente da Associação',
    ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona a quantidade total de mensagens no contexto
        context['total_mensagens'] = ContactMessagesModel.objects.count()
        return context    
    

# Formulário de Contato
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Salva a mensagem no banco de dados
            return render(request, 'app_home/contact_us.html', {
                'form': ContactForm(), 
                'success': True, 
            })
    else:
        form = ContactForm()
    return render(request, 'app_home/contact_us.html', {
        'form': form, 
    })
