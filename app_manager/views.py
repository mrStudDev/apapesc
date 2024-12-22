from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import HttpResponse
import json
from accounts.mixins import GroupPermissionRequiredMixin
from app_associados.models import AssociadoModel
from app_associacao.models import ReparticoesModel, MunicipiosModel, IntegrantesModel
from django.db.models import Count


# Superususers
class DashboardView(GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dashboard.html'
    group_required = 'Superuser'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['is_superuser'] = user.is_superuser
        # Contagens de Associados
        context['total_associados'] = AssociadoModel.objects.count()
        context['associados_ativos'] = AssociadoModel.objects.filter(status="Associado Lista Ativo(a)").count()
        context['associados_aposentados'] = AssociadoModel.objects.filter(status="Associado Lista Aposentado(a)").count()

        # Filtrando categorias específicas
        context['associados_especiais'] = AssociadoModel.objects.filter(status="Cliente Especial").count()
        context['total_candidatos'] = AssociadoModel.objects.filter(status="Candidato(a)").count()

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

        return context


    """def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Contagens de Associados
        context['total_associados'] = AssociadoModel.objects.count()
        context['associados_ativos'] = AssociadoModel.objects.filter(status="Associado Lista Ativo(a)").count()
        context['associados_aposentados'] = AssociadoModel.objects.filter(status="Associado Lista Aposentado(a)").count()

        # Filtrando categorias específicas
        context['associados_especiais'] = AssociadoModel.objects.filter(status="Cliente Especial").count()
        context['total_candidatos'] = AssociadoModel.objects.filter(status="Candidato(a)").count()

        # Sexo biológico
        context['associados_homens'] = AssociadoModel.objects.filter(sexo_biologico="Masculino").count()
        context['associados_mulheres'] = AssociadoModel.objects.filter(sexo_biologico="Feminino").count()
        context['associados_indefinidos'] = AssociadoModel.objects.filter(sexo_biologico="Não declarado").count()

        # Tarefas
        context['tarefas'] = Tarefa.objects.all().order_by('-data_criacao')[:5]
        context['total_tarefas'] = Tarefa.objects.count()

        # Repartições Integrantes e Municípios
        context['total_reparticoes'] = ReparticaoModel.objects.count()
        context['total_integrantes'] = IntegranteAssociacao.objects.count()
        context['total_municipios'] = MunicipiosCircusnscricaoModel.objects.count()
        context['ex_integrantes'] = IntegranteAssociacao.objects.filter(data_saida__isnull=False).count()
        # Para tabela
        context['associados_por_reparticao'] = (
            AssociadoModel.objects
            .values('reparticao__nome_reparticao')
            .annotate(associados_count=Count('id'))
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


        return context

"""

class FinancesView(GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/finances_associacao.html'
    required_groups = 'Superuser'

# --- END SUPER -----#


# Administradores da Associação
class AdminDashboardView(GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dash_administradores.html'
    group_required = 'Admin da Associação'
    
# Delegados da Repartição
class DelegadoDashboardView(GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dash_delegados.html'
    group_required = 'Delegado(a) da Repartição'    

# Auxiliar da Associação    
class AuxiliarAssociacaoDashboardView(GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dash_aux_associacao.html'
    group_required = 'Auxiliar da Associação'
    
# Auxiliar da Repartição 
class AuxiliarReparticaoDashboardView(GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dash_aux_reparticao.html'
    group_required = 'Auxiliar da Repartição'
    
# Diretor da Associação    
class DiretorAssociacaoDashboardView(GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dash_diretores.html'
    group_required = 'Diretor(a) da Associação'
    
# Presidente da Associação    
class PresidenteAssociacaoDashboardView(GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dash_presidente.html'
    group_required = 'Presidente da Associação'
    
# Associado da Associação    
class AssociadoDashboardView(GroupPermissionRequiredMixin, TemplateView):
    template_name = 'app_manager/dash_associado.html'
    group_required = 'Associados da Associação'    