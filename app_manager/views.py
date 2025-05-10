from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import GroupPermissionRequiredMixin
from app_associados.models import AssociadoModel
from app_associacao.models import ReparticoesModel, MunicipiosModel, IntegrantesModel, AssociacaoModel
from app_embarcacoes.models import EmbarcacoesModel
from app_licencas.models import LicencasModel
from app_servicos.models import ServicoAssociadoModel, ServicoExtraAssociadoModel, ExtraAssociadoModel
from app_especies_maritimas.models import EspecieMarinhaModel
from django.db.models.functions import TruncMonth, ExtractYear, ExtractMonth
from collections import OrderedDict
from django.db.models import Count
import json
from app_home.models import LeadInformacoes, ContactMessagesModel
from app_tarefas.models import TarefaModel, GuiaINSSModel, LancamentoINSSModel
from app_articles.models import ArticlesModel
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from app_beneficios.models import ControleBeneficioModel, BeneficioModel


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
        
        # Artigos
        context['articles'] = ArticlesModel.objects.all().order_by('-date_created')[:5]
        
        context['total_articles'] = ArticlesModel.objects.count()
        
        context['total_licencas'] = LicencasModel.objects.count()   
             
        context['total_embarcacoes'] = EmbarcacoesModel.objects.count()
        context['embarcacoes_motor'] = EmbarcacoesModel.objects.filter(tipo_propulsao__nome__iexact='Motor').count()
        context['embarcacoes_vela'] = EmbarcacoesModel.objects.filter(tipo_propulsao__nome__iexact='Vela').count()


        # Serviços para associados
        context['total_servicos_associados'] = ServicoAssociadoModel.objects.count()
    
        # Serviços para extra-associados
        context['total_servicos_extras'] = ServicoExtraAssociadoModel.objects.count()

        # Serviços para associados (limite 2)
        context['servicos_associados_recentes'] = (
            ServicoAssociadoModel.objects
            .select_related('associado', 'tipo_servico')
            .order_by('-data_inicio')[:5]
        )
        # Serviços para extra-associados (limite 2)
        context['servicos_extras_recentes'] = (
            ServicoExtraAssociadoModel.objects
            .select_related('extra_associado', 'tipo_servico')
            .order_by('-data_inicio')[:5]
        )
        # Serviços para Extra-associados (limite 2)
        context['total_extra_associados'] = ExtraAssociadoModel.objects.count()

        # Dois serviços mais recentes de extra associados
        context['servicos_extras_recentes'] = (
            ServicoExtraAssociadoModel.objects
            .filter(extra_associado__isnull=False)
            .select_related('extra_associado', 'tipo_servico')
            .order_by('-data_inicio')[:3]
        )
        # Agrupamento por mês/ano
        servicos_associados = (
            ServicoAssociadoModel.objects
            .annotate(mes=TruncMonth('data_inicio'))
            .values('mes')
            .annotate(qtd=Count('id'))
            .order_by('mes')
        )

        servicos_extra = (
            ServicoExtraAssociadoModel.objects
            .annotate(mes=TruncMonth('data_inicio'))
            .values('mes')
            .annotate(qtd=Count('id'))
            .order_by('mes')
        )

        # Meses únicos e ordenados
        meses = sorted(set(
            [x['mes'] for x in servicos_associados if x['mes']] +
            [x['mes'] for x in servicos_extra if x['mes']
        ]))

        # Inicializa com 0 em vez de None
        dados_associado = {m.strftime('%Y-%m'): 0 for m in meses}
        dados_extra = {m.strftime('%Y-%m'): 0 for m in meses}

        # Preenche os dados
        for s in servicos_associados:
            if s['mes']:
                dados_associado[s['mes'].strftime('%Y-%m')] = s['qtd']

        for s in servicos_extra:
            if s['mes']:
                dados_extra[s['mes'].strftime('%Y-%m')] = s['qtd']

        # Garante a ordem correta e formatação
        labels = [m.strftime('%b/%Y') for m in meses]  # Formato "Jan/2023"
        valores_associado = [dados_associado[m.strftime('%Y-%m')] for m in meses]
        valores_extra = [dados_extra[m.strftime('%Y-%m')] for m in meses]

        context['grafico_servicos_labels'] = json.dumps(labels)
        context['grafico_servicos_associado'] = json.dumps(valores_associado)
        context['grafico_servicos_extra'] = json.dumps(valores_extra)

        # 🔹 Define a queryset Associados Grafico
        associados = AssociadoModel.objects.filter(data_filiacao__isnull=False)
         # 🔹 Conta os associados por ano e mês de filiação
        associados_por_periodo = (
            associados.annotate(ano=ExtractYear('data_filiacao'), mes=ExtractMonth('data_filiacao'))
            .values('ano', 'mes')
            .annotate(total=Count('id'))
            .order_by('ano', 'mes')
        )
        # 🔹 Transforma os dados para o gráfico
        anos_meses = [f"{dado['ano']}-{str(dado['mes']).zfill(2)}" for dado in associados_por_periodo]
        totais = [dado["total"] for dado in associados_por_periodo]
        # 🔹 Garante que os dados estejam sempre preenchidos
        context["anos_meses_filiacao"] = json.dumps(anos_meses if anos_meses else ["2025-01"])
        context["total_associados_por_periodo"] = json.dumps(totais if totais else [0])

        # Espécies Marinhas
        context['total_especies'] = EspecieMarinhaModel.objects.count()
        context['ultimas_especies'] = EspecieMarinhaModel.objects.order_by('-id')[:5]

        # 1. Último lançamento INSS
        ultimo_lancamento = LancamentoINSSModel.objects.order_by('-ano', '-mes').first()

        # Default para exibição segura no template
        context['ultimo_lancamento'] = ultimo_lancamento

        # 2. Total associados que recolhem INSS
        recolhe_inss_qs = AssociadoModel.objects.filter(recolhe_inss='Sim')
        context['total_associados_inss'] = recolhe_inss_qs.count()

        # 3. Contagem de observações apenas no último lançamento (caso exista)
        if ultimo_lancamento:
            guias_ultimas = GuiaINSSModel.objects.filter(lancamento=ultimo_lancamento)
            
            observacoes_counts = guias_ultimas.values('observacoes').annotate(total=Count('id'))
            observacoes_map = {obs['observacoes']: obs['total'] for obs in observacoes_counts}

            context['inss_observacoes'] = observacoes_map
        else:
            context['inss_observacoes'] = {}

        # 🔹 Lista de status possíveis
        status_labels = dict(ControleBeneficioModel.STATUS_CHOICES)

        # 🔹 Lista de benefícios
        beneficios = BeneficioModel.objects.all().order_by('nome')

        beneficio_status_data = []

        for beneficio in beneficios:
            controles = ControleBeneficioModel.objects.filter(beneficio=beneficio)
            total_por_status = controles.values('status_pedido').annotate(total=Count('id'))
            total_por_status = controles.values('status_pedido').annotate(total=Count('id'))
            
            # Mapeia os resultados
            status_dict = {s['status_pedido']: s['total'] for s in total_por_status}
            total_geral = sum(status_dict.values()) 
            
            beneficio_status_data.append({
                'nome': dict(BeneficioModel.BENEFICIO_CHOICES).get(beneficio.nome, beneficio.nome),
                'estado': beneficio.estado,
                'ano': beneficio.ano_concessao,
                'status': status_dict,
                'total': total_geral  # 👈 aqui
            })

        context['beneficio_status_labels'] = status_labels
        context['beneficio_status_data'] = beneficio_status_data

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
    
    
