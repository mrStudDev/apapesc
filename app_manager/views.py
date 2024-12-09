from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import HttpResponse
import json
#from app_associados.models import AssociadoModel, ReparticaoModel, MunicipiosCircusnscricaoModel
#from django.db.models import Count
#from common.permissions import GroupPermissionRequiredMixin
#from app_tarefas.models import Tarefa
#from app_usuarios.models import IntegranteApapesc



#GroupPermissionRequiredMixin, 

class DashboardView(TemplateView):
    template_name = 'app_manager/dashboard.html'
    #required_groups = ['Admin', 'Adm_Apapesc']

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
        context['total_integrantes'] = IntegranteApapesc.objects.count()
        context['total_municipios'] = MunicipiosCircusnscricaoModel.objects.count()
        context['ex_integrantes'] = IntegranteApapesc.objects.filter(data_saida__isnull=False).count()
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

#GroupPermissionRequiredMixin,

class FinancesView( TemplateView):
    template_name = 'app_manager/finances_apapesc.html'
    #required_groups = ['Admin', 'Adm_Apapesc']

