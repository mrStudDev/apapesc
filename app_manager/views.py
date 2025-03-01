from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import GroupPermissionRequiredMixin
from app_associados.models import AssociadoModel
from app_associacao.models import ReparticoesModel, MunicipiosModel, IntegrantesModel, AssociacaoModel
from django.db.models import Count
import json
from app_home.models import LeadInformacoes, ContactMessagesModel
from app_tarefas.models import TarefaModel
from app_articles.models import ArticlesModel
from django.shortcuts import get_object_or_404


# Superususers dashboard.html
class DashboardView(LoginRequiredMixin, GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dashboard.html'
    group_required = ['Superuser']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['is_superuser'] = user.is_superuser
        
        # Filtrando categorias específicas
        context['total_associados'] = AssociadoModel.objects.count()
        context['associados_ativos'] = AssociadoModel.objects.filter(status="Associado Lista Ativo(a)").count()
        context['associados_aposentados'] = AssociadoModel.objects.filter(status="Associado Lista Aposentado(a)").count()
        context['associados_especiais'] = AssociadoModel.objects.filter(status="Cliente Especial").count()
        context['total_candidatos'] = AssociadoModel.objects.filter(status="Candidato(a)").count()
        context['total_desassociados'] = AssociadoModel.objects.filter(status="Desassociado(a)").count()

        # Sexo biológico
        context['associados_homens'] = AssociadoModel.objects.filter(sexo_biologico="Masculino").count()
        context['associados_mulheres'] = AssociadoModel.objects.filter(sexo_biologico="Feminino").count()
        context['associados_indefinidos'] = AssociadoModel.objects.filter(sexo_biologico="Não declarado").count()

        # Associados por Repartição e municípios e Municípios
        context['total_integrantes'] = IntegrantesModel.objects.count()
        context['ex_integrantes'] = IntegrantesModel.objects.filter(data_saida__isnull=False).count()

       # Para tabela
       # Associados por Associação
        context['associados_por_associacao'] = (
            AssociadoModel.objects
            .values('associacao', 'associacao__nome_fantasia')  # Inclua o ID da associação e o nome fantasia
            .annotate(associados_count=Count('id'))  # Conte os associados
            .order_by('associacao__nome_fantasia')
        )
       # Associados por repartição
        context['associados_por_reparticao'] = (
            AssociadoModel.objects
            .values('reparticao', 'reparticao__nome_reparticao')  # Inclua o ID da repartição e seu nome
            .annotate(associados_count=Count('id'))  # Conte os associados
            .order_by('reparticao__nome_reparticao')
        )
        # Municípios de Circunscrição
        context['associados_por_municipio_circunscricao'] = (
            AssociadoModel.objects
            .values('municipio_circunscricao__municipio')
            .annotate(associados_count=Count('id'))
            .order_by('municipio_circunscricao__municipio')
        )
        # Municípios de Circunscrição (Gráfico)
        associados_por_municipio_circunscricao_json = (
            AssociadoModel.objects
            .values('municipio_circunscricao__municipio')
            .annotate(associados_count=Count('id'))
            .order_by('municipio_circunscricao__municipio')
        )
        context['associados_por_municipio_circunscricao_json'] = json.dumps(list(associados_por_municipio_circunscricao_json))

        # Para o gráfico
        associados_por_reparticao_json = list(context['associados_por_reparticao'])
        context['associados_por_reparticao_json'] = json.dumps(associados_por_reparticao_json)

        # Associados Por Status
        associados_por_status = (
            AssociadoModel.objects
            .values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )
        context['associados_por_status_json'] = json.dumps(list(associados_por_status))
        
        # Leads Mensagens - Home
        context['leads'] = LeadInformacoes.objects.all().order_by('-created_at')
        context['total_leads'] = LeadInformacoes.objects.count()
        
        # Contato Mensagens - Home
        context['contato_mensagens'] = ContactMessagesModel.objects.all().order_by('-created_at')
        context['total_mensagens'] = ContactMessagesModel.objects.count()
        
        # Tarefas
        context['tarefas'] = TarefaModel.objects.all().order_by('-data_criacao')[:5]
        context['total_tarefas'] = TarefaModel.objects.count()
        
        # Tarefas
        context['articles'] = ArticlesModel.objects.all().order_by('-date_created')[:5]
        context['total_articles'] = ArticlesModel.objects.count()
        

        return context



from django.db.models import Prefetch


from django.db.models import Count, Prefetch, Q
from django.views.generic import ListView
from app_associacao.models import AssociacaoModel, ReparticoesModel
from app_associados.models import AssociadoModel

class QuadroAssociadosView(ListView):
    template_name = 'app_manager/quadro_associados.html'
    context_object_name = 'associacoes'
    model = AssociacaoModel

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Prefetch com anotações para contar associados por status
        reparticoes_com_contagem = Prefetch(
            'reparticoes',
            queryset=ReparticoesModel.objects.annotate(
                qtd_associados=Count('reparticoes_associados'),
                qtd_ativos=Count('reparticoes_associados', filter=Q(reparticoes_associados__status='Associado Lista Ativo(a)')),
                qtd_aposentados=Count('reparticoes_associados', filter=Q(reparticoes_associados__status='Associado Lista Aposentado(a)')),
                qtd_candidatos=Count('reparticoes_associados', filter=Q(reparticoes_associados__status='Candidato(a)')),
                qtd_clientes_especiais=Count('reparticoes_associados', filter=Q(reparticoes_associados__status='Cliente Especial')),
                qtd_desassociados=Count('reparticoes_associados', filter=Q(reparticoes_associados__status='Desassociado(a)')),
            )
        )

        associacoes = AssociacaoModel.objects.prefetch_related(reparticoes_com_contagem)

        associacoes_data = []
        for associacao in associacoes:
            associacao_info = {
                'nome': associacao.nome_fantasia,
                'reparticoes': [
                    {
                        'nome': reparticao.nome_reparticao,
                        'qtd_associados': reparticao.qtd_associados,
                        'status': {
                            'ativos': reparticao.qtd_ativos,
                            'aposentados': reparticao.qtd_aposentados,
                            'candidatos': reparticao.qtd_candidatos,
                            'clientes_especiais': reparticao.qtd_clientes_especiais,
                            'desassociados': reparticao.qtd_desassociados,
                        }
                    }
                    for reparticao in associacao.reparticoes.all()
                ]
            }
            associacoes_data.append(associacao_info)

        context['associacoes_data'] = associacoes_data
        return context

    
# Administradores da Associação
class AdminDashboardView(LoginRequiredMixin, GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dash_administradores.html'
    group_required = 'Admin da Associação'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Identificar a associação do usuário logado
        user = self.request.user
        integrante = get_object_or_404(IntegrantesModel, user=user)
        associacao = integrante.associacao
        
        # Filtrar dados relacionados à associação
        associados = AssociadoModel.objects.filter(associacao=associacao)
        reparticoes = ReparticoesModel.objects.filter(associacao=associacao)
        integrantes = IntegrantesModel.objects.filter(associacao=associacao)
        
        # Contagens específicas
        context['total_associados'] = associados.count()
        
        context['associados_ativos'] = associados.filter(status='ativo').count()
        context['associados_aposentados'] = associados.filter(status='aposentado').count()
        context['associados_especiais'] = associados.filter(status='especial').count()
        context['total_candidatos'] = associados.filter(status='candidato').count()
        
        # Adiciona repartições e integrantes ao contexto
        context['total_reparticoes'] = reparticoes.count()
        context['total_integrantes'] = integrantes.count()

        return context
    
# Delegados da Repartição
class DelegadoDashboardView(LoginRequiredMixin, GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dash_delegados.html'
    group_required = 'Delegado(a) da Repartição'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        delegado = IntegrantesModel.objects.get(user=user)
        reparticao = delegado.reparticao

        # Totais por repartição
        total_associados = AssociadoModel.objects.filter(reparticao=reparticao).count()

        # Totais por status dentro da repartição
        associados_ativos = AssociadoModel.objects.filter(reparticao=reparticao, status='ativo').count()
        associados_aposentados = AssociadoModel.objects.filter(reparticao=reparticao, status='aposentado').count()
        associados_especiais = AssociadoModel.objects.filter(reparticao=reparticao, status='especial').count()

        # Adiciona os dados ao contexto
        context.update({
            'reparticao': reparticao,
            'total_associados': total_associados,
            'associados_ativos': associados_ativos,
            'associados_aposentados': associados_aposentados,
            'associados_especiais': associados_especiais,
        })

        return context
 
 
# Diretor da Associação    
class DiretorAssociacaoDashboardView(LoginRequiredMixin, GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dash_diretores.html'
    group_required = 'Diretor(a) da Associação'
    
# Presidente da Associação    
class PresidenteAssociacaoDashboardView(LoginRequiredMixin, GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dash_presidente.html'
    group_required = 'Presidente da Associação'
    
# Auxiliar da Associação    
class AuxiliarAssociacaoDashboardView(LoginRequiredMixin, GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dash_aux_associacao.html'
    group_required = 'Auxiliar da Associação'
    
# Auxiliar da Repartição 
class AuxiliarReparticaoDashboardView(LoginRequiredMixin, GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dash_aux_reparticao.html'
    group_required = 'Auxiliar da Repartição'
    

# Associado da Associação    
class AssociadoDashboardView(LoginRequiredMixin, GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dash_associado.html'
    group_required = 'Associados da Associação'    
    
class UserVipDashboardView(LoginRequiredMixin, GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dash_user_vip.html'    
    group_required = 'User Vip'
    
    
