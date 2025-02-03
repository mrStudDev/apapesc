from django.shortcuts import render, get_object_or_404, redirect
from app_finances.models import AnuidadeModel, AnuidadeAssociado, Pagamento
from app_associados.models import AssociadoModel
from django.db import models
from django.views.generic import DetailView, TemplateView, ListView
from django.contrib import messages
from django.views import View
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Sum, Count
from django.utils import timezone
from app_associacao.models import AssociacaoModel
from .models import DespesaAssociacaoModel


def lista_anuidades(request):
    # Obter o ano selecionado pelo usuário
    ano_selecionado = request.GET.get('ano')

    # Obter todos os anos de anuidades já cadastrados
    anos_disponiveis = AnuidadeModel.objects.values_list('ano', flat=True).distinct().order_by('ano')

    # Filtrar os dados das anuidades com base no ano selecionado
    if ano_selecionado:
        anuidade = get_object_or_404(AnuidadeModel, ano=ano_selecionado)
        anuidades_associados = AnuidadeAssociado.objects.filter(anuidade=anuidade).select_related('associado')

        # Adicionar informações extras para cada associado
        for anuidade_assoc in anuidades_associados:
            # Calcular total de pagamentos para o ano atual
            pagamentos_ano = anuidade_assoc.pagamentos.aggregate(total_pago=Sum('valor'))['total_pago'] or Decimal('0.00')
            anuidade_assoc.total_pago_ano = pagamentos_ano

            # Calcular o saldo devedor total de todas as anuidades do associado
            total_debito = AnuidadeAssociado.objects.filter(associado=anuidade_assoc.associado, pago=False).aggregate(
                saldo_devedor=Sum('valor_pro_rata') - Sum('valor_pago')
            )['saldo_devedor'] or Decimal('0.00')
            anuidade_assoc.saldo_devedor_total = total_debito

    else:
        anuidades_associados = []

    context = {
        'anos_disponiveis': anos_disponiveis,
        'ano_selecionado': ano_selecionado,
        'anuidades_associados': anuidades_associados,
    }

    return render(request, 'app_finances/list_anuidades.html', context)



class FinanceiroAssociadoDetailView(DetailView):
    model = AssociadoModel
    template_name = 'app_finances/financeiro_associado.html'
    context_object_name = 'associado'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        associado = self.get_object()

        # Obter todas as anuidades relacionadas
        anuidades = associado.anuidades_associados.select_related('anuidade').order_by('-anuidade__ano')

        # Calcular os totais e valores detalhados
        total_anuidades = 0
        total_pago = 0
        detalhes_anuidades = []

        for anuidade in anuidades:
            valor_pago = anuidade.pagamentos.aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
            saldo = anuidade.valor_pro_rata - valor_pago

            total_anuidades += anuidade.valor_pro_rata
            total_pago += valor_pago

            detalhes_anuidades.append({
                'ano': anuidade.anuidade.ano,
                'valor_total': anuidade.valor_pro_rata,
                'valor_pago': valor_pago,
                'saldo': saldo,
                'anuidade': anuidade,
            })
        # Buscar os pagamentos relacionados ao associado        
        pagamentos = Pagamento.objects.filter(anuidade_associado__associado=associado).select_related('registrado_por')
        
        context['anuidades_associado'] = detalhes_anuidades
        context['total_anuidades'] = total_anuidades
        context['total_pago'] = total_pago
        context['saldo_total'] = total_anuidades - total_pago
        context['pagamentos'] = pagamentos
        
        return context




@method_decorator(login_required, name='dispatch')
class DarBaixaAnuidadeView(View):
    def post(self, request, pk):
        anuidade_assoc = get_object_or_404(AnuidadeAssociado, pk=pk)
        
        # Obtem o valor enviado no formulário
        valor_baixa = Decimal(request.POST.get('valor_baixa', '0.00'))

        if valor_baixa <= 0:
            messages.error(request, "O valor para dar baixa deve ser maior que zero.")
        else:
            # Cria o pagamento manualmente antes de chamar o método 'dar_baixa'
            Pagamento.objects.create(
                anuidade_associado=anuidade_assoc,
                valor=valor_baixa,
                registrado_por=request.user
            )

            # Aplica a baixa no valor da anuidade
            anuidade_assoc.dar_baixa(valor_baixa)

            # Calcula o saldo restante
            saldo = anuidade_assoc.calcular_saldo()

            if saldo == 0:
                messages.success(request, "Pagamento concluído! A anuidade foi quitada.")
            else:
                messages.success(request, f"Baixa registrada! Saldo restante: R$ {saldo:.2f}")

        return redirect('app_finances:financeiro_associado', anuidade_assoc.associado.id)


class ResumoFinanceiroView(TemplateView):
    template_name = 'app_finances/finances_super.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Data atual
        data_atual = timezone.now().date()

        # Total geral de associados
        total_associados = AssociadoModel.objects.count()
        
        # Resumo geral de despesas
        total_despesas = DespesaAssociacaoModel.objects.aggregate(total=Sum('valor'))['total'] or 0

        # Resumo de despesas por associação (sem vínculo com associados)
        despesas_por_associacao = (
            DespesaAssociacaoModel.objects
            .values('associacao__nome_fantasia', 'associacao__id')
            .annotate(
                total_despesas=Sum('valor')
            )
            .order_by('associacao__nome_fantasia')
        )
        
        # Totais financeiros gerais
        receita_total = AnuidadeAssociado.objects.aggregate(total_pago=Sum('valor_pago'))['total_pago'] or Decimal('0.00')
        saldo_pendente = AnuidadeAssociado.objects.aggregate(
            saldo_devedor=Sum('valor_pro_rata') - Sum('valor_pago')
        )['saldo_devedor'] or Decimal('0.00')

        # Associados em dia e em atraso
        associados_em_dia = AnuidadeAssociado.objects.filter(pago=True).values('associado').distinct().count()
        associados_em_atraso = total_associados - associados_em_dia

        # Informações por associação (anuidades e associados)
        associacoes_data = []
        associacoes = AssociacaoModel.objects.all()

        for associacao in associacoes:
            associados = AssociadoModel.objects.filter(associacao=associacao)
            total_associados_assoc = associados.count()

            # Receita e saldo pendente por associação
            receita_assoc = AnuidadeAssociado.objects.filter(associado__in=associados).aggregate(
                total_receita=Sum('valor_pago')
            )['total_receita'] or Decimal('0.00')

            saldo_assoc = AnuidadeAssociado.objects.filter(associado__in=associados).aggregate(
                saldo_pendente=Sum('valor_pro_rata') - Sum('valor_pago')
            )['saldo_pendente'] or Decimal('0.00')

            associacoes_data.append({
                'nome': associacao.nome_fantasia,
                'total_associados': total_associados_assoc,
                'receita_total': receita_assoc,
                'saldo_pendente': saldo_assoc,
            })

        # Adicionar informações ao contexto
        context.update({
            'total_associados': total_associados,
            'associados_em_dia': associados_em_dia,
            'associados_em_atraso': associados_em_atraso,
            'receita_total': receita_total,
            'saldo_pendente': saldo_pendente,
            'data_atual': data_atual,
            'associacoes_data': associacoes_data,
            'total_despesas': total_despesas,
            'despesas_por_associacao': despesas_por_associacao,
        })

        return context




class ListDespesasView(ListView):
    model = DespesaAssociacaoModel
    template_name = 'app_finances/list_despesas.html'
    context_object_name = 'despesas'

    def get_queryset(self):
        queryset = DespesaAssociacaoModel.objects.select_related('associacao', 'tipo_despesa')

        # Filtrando por associação, ano e mês
        associacao_id = self.request.GET.get('associacao')
        ano = self.request.GET.get('ano')
        mes = self.request.GET.get('mes')

        if associacao_id:
            queryset = queryset.filter(associacao_id=associacao_id)
        if ano:
            queryset = queryset.filter(data_despesa__year=ano)
        if mes:
            queryset = queryset.filter(data_despesa__month=mes)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        despesas_filtradas = self.get_queryset()

        # Recuperar o ano, mês e associação do GET
        ano = self.request.GET.get('ano')
        mes = self.request.GET.get('mes')
        associacao_id = self.request.GET.get('associacao')

        # Calculando o total das despesas filtradas
        total_despesas = despesas_filtradas.aggregate(total=Sum('valor'))['total'] or 0

        # Lista de nomes dos meses
        meses_nomes = [
            (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"), (5, "Maio"), 
            (6, "Junho"), (7, "Julho"), (8, "Agosto"), (9, "Setembro"), (10, "Outubro"), 
            (11, "Novembro"), (12, "Dezembro")
        ]

        # Passando informações ao contexto
        context['associacoes'] = AssociacaoModel.objects.all()
        context['anos'] = despesas_filtradas.dates('data_despesa', 'year')
        context['meses'] = meses_nomes
        context['total_despesas'] = total_despesas
        context['associacao_selecionada'] = associacao_id
        context['ano_selecionado'] = ano
        context['mes_selecionado'] = mes
        return context
