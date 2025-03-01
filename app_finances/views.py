from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Sum, Count, Q
from django.contrib import messages
from django.db import models
from decimal import Decimal
from django.utils.timezone import now

from django.views.generic import DetailView, TemplateView, ListView, CreateView, UpdateView
from django.views import View
from django.db.models import Value, F
from django.db.models.functions import Concat, Lower

from .models import AnuidadeModel, AnuidadeAssociado, Pagamento, DescontoAnuidade
from app_associados.models import AssociadoModel
from app_associacao.models import AssociacaoModel

from .models import DespesaAssociacaoModel
from .forms import AnuidadeForm

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps



def lista_anuidades(request):
    # Obter o ano selecionado pelo usuário
    ano_selecionado = request.GET.get('ano')

    # Obter todos os anos de anuidades já cadastrados
    anos_disponiveis = AnuidadeModel.objects.values_list('ano', flat=True).distinct().order_by('ano')

    # Filtrar os dados das anuidades com base no ano selecionado
    if ano_selecionado:
        anuidade = get_object_or_404(AnuidadeModel, ano=ano_selecionado)
        anuidades_associados = (
            AnuidadeAssociado.objects.filter(anuidade=anuidade)
            .select_related('associado__user')
            .annotate(
                full_name=Concat(
                    F('associado__user__first_name'),
                    Value(' '),
                    F('associado__user__last_name')
                )
            )
            .order_by('full_name')
        )

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
        total_descontos = 0
        detalhes_anuidades = []

        for anuidade in anuidades:
            valor_pago = anuidade.pagamentos.aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
            valor_desconto = anuidade.descontos.aggregate(total=Sum('valor_desconto'))['total'] or Decimal('0.00')
            saldo = anuidade.valor_pro_rata - valor_pago - valor_desconto

            total_anuidades += anuidade.valor_pro_rata
            total_pago += valor_pago
            total_descontos += valor_desconto

            detalhes_anuidades.append({
                'ano': anuidade.anuidade.ano,
                'valor_total': anuidade.valor_pro_rata,
                'valor_pago': valor_pago,
                'valor_desconto': valor_desconto,
                'saldo': saldo,
                'anuidade': anuidade,
            })

        # Buscar os pagamentos relacionados ao associado        
        pagamentos = Pagamento.objects.filter(anuidade_associado__associado=associado).select_related('registrado_por')

        # Buscar os descontos relacionados ao associado        
        descontos = DescontoAnuidade.objects.filter(anuidade_associado__associado=associado).select_related('concedido_por')

        # Criar lista única de eventos financeiros (pagamentos e descontos)
        eventos_financeiros = []
        for pagamento in pagamentos:
            eventos_financeiros.append({
                'tipo': 'pagamento',
                'data': pagamento.data_pagamento,  # Já é do tipo date
                'valor': pagamento.valor,
                'ano': pagamento.anuidade_associado.anuidade.ano,
                'registrado_por': pagamento.registrado_por,
                'motivo': None  # Pagamento não tem motivo
            })

        for desconto in descontos:
            eventos_financeiros.append({
                'tipo': 'desconto',
                'data': desconto.data_concessao.date(),  # Converte datetime para date
                'valor': desconto.valor_desconto,
                'ano': desconto.anuidade_associado.anuidade.ano,
                'registrado_por': desconto.concedido_por,
                'motivo': desconto.motivo  # Inclui o motivo do desconto
            })

        # Ordenar os eventos por data (mais recente primeiro)
        eventos_financeiros.sort(key=lambda x: x['data'], reverse=True)

        context.update({
            'anuidades_associado': detalhes_anuidades,
            'total_anuidades': total_anuidades,
            'total_pago': total_pago,
            'total_descontos': total_descontos,
            'saldo_total': total_anuidades - total_pago - total_descontos,
            'pagamentos': pagamentos,
            'descontos': descontos,
            'eventos_financeiros': eventos_financeiros
        })
        
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


# Lista Triangular de Condições
def associados_triangulo_view(request):
    ano_atual = now().year

    # Obter o valor da anuidade do ano atual
    anuidade_atual = AnuidadeModel.objects.filter(ano=ano_atual).first()
    valor_anuidade_atual = anuidade_atual.valor_anuidade if anuidade_atual else Decimal('0.00')

    # Associados em dia (todas as anuidades quitadas até o ano vigente)
    associados_em_dia = (
        AssociadoModel.objects.filter(
            anuidades_associados__pago=True, 
            anuidades_associados__anuidade__ano=ano_atual
        )
        .distinct()
    )

    # Associados com anuidades do ano vigente em aberto
    associados_a_pagar = (
        AssociadoModel.objects.filter(
            anuidades_associados__anuidade__ano=ano_atual,
            anuidades_associados__pago=False
        )
        .annotate(valor_anuidade=Sum('anuidades_associados__valor_pro_rata'))
    )

    # Associados com anuidades de anos anteriores em atraso
    associados_atrasados = (
        AssociadoModel.objects.filter(
            anuidades_associados__anuidade__ano__lt=ano_atual,
            anuidades_associados__pago=False
        )
        .annotate(valor_debito=Sum('anuidades_associados__valor_pro_rata') - Sum('anuidades_associados__valor_pago'))
    )

    context = {
        'associados_em_dia': associados_em_dia,
        'associados_a_pagar': associados_a_pagar,
        'associados_atrasados': associados_atrasados,
        'ano_atual': ano_atual,
        'valor_anuidade_atual': valor_anuidade_atual,  # Adicionando o valor da anuidade ao contexto
    }

    return render(request, 'app_finances/tri_condictions.html', context)


def aplicar_anuidade(request, associado_id):
    associado = get_object_or_404(AssociadoModel, id=associado_id)

    # Verifica se o status permite aplicar anuidade
    if associado.status in ["Cliente Especial", "Desassociado(a)"]:
        messages.error(request, "Este associado não pode receber anuidade.")
        return JsonResponse({"success": False, "message": "Status do associado não permite anuidade."}, status=400)

    ano_atual = timezone.now().year

    # 📌 Buscar todas as anuidades disponíveis desde o ano de filiação
    anuidades = AnuidadeModel.objects.filter(ano__gte=associado.data_filiacao.year, ano__lte=ano_atual).order_by("ano")

    if not anuidades.exists():
        messages.error(request, "Nenhuma anuidade encontrada para os anos pendentes.")
        return JsonResponse({"success": False, "message": "Nenhuma anuidade encontrada."}, status=400)

    aplicadas = []
    with transaction.atomic():
        for anuidade in anuidades:
            # Evita duplicação de anuidade para esse associado
            if AnuidadeAssociado.objects.filter(anuidade=anuidade, associado=associado).exists():
                continue  # Pula se a anuidade já existe

            # 📌 Cálculo pró-rata apenas no primeiro ano
            if anuidade.ano == associado.data_filiacao.year:
                meses_restantes = associado.calcular_meses_validos(anuidade.ano)
                valor_a_cobrar = round((anuidade.valor_anuidade / Decimal(12)) * Decimal(meses_restantes), 2)
            else:
                valor_a_cobrar = anuidade.valor_anuidade  # Anos seguintes, cobrança total

            # Criar o registro de anuidade do associado
            AnuidadeAssociado.objects.create(
                anuidade=anuidade,
                associado=associado,
                valor_pro_rata=valor_a_cobrar
            )
            aplicadas.append(anuidade.ano)

    if aplicadas:
        messages.success(request, f"Anuidade aplicada para os anos: {', '.join(map(str, aplicadas))}.")
    else:
        messages.error(request, "As anuidades já haviam sido aplicadas anteriormente.")

    # 🔄 Retorna para a mesma página do associado
    return redirect('app_associados:single_associado', pk=associado.id)


@login_required
@csrf_exempt
def conceder_desconto(request, anuidade_associado_id):
    """
    Aplica um desconto na anuidade do associado sem alterar o valor original da anuidade.
    Apenas reduz o saldo devedor.
    """
    anuidade_associado = get_object_or_404(AnuidadeAssociado, id=anuidade_associado_id)

    if request.method == "POST":
        valor_desconto = Decimal(request.POST.get("valor_desconto", "0.00"))
        motivo = request.POST.get("motivo", "").strip()

        if valor_desconto <= 0:
            messages.error(request, "O valor do desconto deve ser maior que zero.")
            return redirect('app_finances:financeiro_associado', pk=anuidade_associado.associado.id)

        if not motivo:
            messages.error(request, "É obrigatório informar um motivo para o desconto.")
            return redirect('app_finances:financeiro_associado', pk=anuidade_associado.associado.id)

        with transaction.atomic():
            # Criar o registro do desconto sem alterar o valor da anuidade
            desconto = DescontoAnuidade.objects.create(
                anuidade_associado=anuidade_associado,
                valor_desconto=valor_desconto,
                motivo=motivo,
                concedido_por=request.user
            )

            # 🔥 Em vez de reduzir o valor da anuidade, apenas reduz o saldo devedor
            saldo_atual = anuidade_associado.calcular_saldo()
            novo_saldo = max(saldo_atual - valor_desconto, Decimal('0.00'))  # Evita saldo negativo

            anuidade_associado.valor_pago += valor_desconto  # O desconto age como um pagamento
            if anuidade_associado.valor_pago >= anuidade_associado.valor_pro_rata:
                anuidade_associado.pago = True  # Se quitado, marca como pago

            anuidade_associado.save()

            messages.success(request, f"Desconto de R$ {valor_desconto} aplicado com sucesso!")

    return redirect('app_finances:financeiro_associado', pk=anuidade_associado.associado.id)


# Lista de descontos - Página
class DescontosAnuidadesView(TemplateView):
    template_name = 'app_finances/descontos_anuidades.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obter o ano selecionado pelo usuário
        ano_selecionado = self.request.GET.get('ano')

        # Obter todos os anos de anuidades já cadastrados
        anos_disponiveis = AnuidadeModel.objects.values_list('ano', flat=True).distinct().order_by('-ano')

        # Filtrar os descontos por ano selecionado
        descontos_associados = DescontoAnuidade.objects.all().select_related(
            'anuidade_associado__associado__user', 'anuidade_associado__anuidade', 'concedido_por'
        ).order_by('-anuidade_associado__anuidade__ano')

        if ano_selecionado:
            descontos_associados = descontos_associados.filter(anuidade_associado__anuidade__ano=ano_selecionado)

        # Montar a lista de descontos organizados por associado e ano
        descontos_por_associado = {}
        for desconto in descontos_associados:
            associado = desconto.anuidade_associado.associado
            ano = desconto.anuidade_associado.anuidade.ano

            if associado not in descontos_por_associado:
                descontos_por_associado[associado] = {}

            if ano not in descontos_por_associado[associado]:
                descontos_por_associado[associado][ano] = {
                    'total_desconto': Decimal('0.00'),
                    'detalhes': []
                }

            descontos_por_associado[associado][ano]['total_desconto'] += desconto.valor_desconto
            descontos_por_associado[associado][ano]['detalhes'].append({
                'valor': desconto.valor_desconto,
                'motivo': desconto.motivo,
                'concedido_por': desconto.concedido_por.get_full_name() if desconto.concedido_por else "Sistema",
                'data': desconto.data_concessao
            })

        context.update({
            'anos_disponiveis': anos_disponiveis,
            'ano_selecionado': ano_selecionado,
            'descontos_por_associado': descontos_por_associado,
        })

        return context



class CreateAnuidadeView(CreateView):
    model = AnuidadeModel
    form_class = AnuidadeForm
    template_name = 'app_finances/create_anuidade.html'
    success_url = reverse_lazy('app_finances:create_anuidade')

    def form_valid(self, form):
        """
        Após salvar a anuidade, aplica apenas aos associados com status:
        - "Associado Lista Ativo(a)"
        - "Associado Lista Aposentado(a)"
        """
        response = super().form_valid(form)  # Salva a anuidade primeiro
        anuidade = self.object  # Obtém a anuidade recém-criada

        # ✅ Obtém os modelos corretamente usando apps.get_model
        AssociadoModel = apps.get_model('app_associados', 'AssociadoModel')
        AnuidadeAssociado = apps.get_model('app_finances', 'AnuidadeAssociado')

        # ✅ 🚀 Corrigindo a filtragem dos associados válidos 🚀
        associados_validos = AssociadoModel.objects.filter(
            status__exact="Associado Lista Ativo(a)"
        ) | AssociadoModel.objects.filter(
            status__exact="Associado Lista Aposentado(a)"
        )

        aplicadas = []
        with transaction.atomic():
            for associado in associados_validos:
                # Verifica se a anuidade já foi aplicada para evitar duplicação
                if not AnuidadeAssociado.objects.filter(anuidade=anuidade, associado=associado).exists():
                    AnuidadeAssociado.objects.create(
                        anuidade=anuidade,
                        associado=associado,
                        valor_pro_rata=anuidade.valor_anuidade  # Valor cheio para anos normais
                    )
                    aplicadas.append(associado.user.get_full_name() if associado.user else associado.id)

        messages.success(self.request, f"Anuidade {anuidade.ano} criada e aplicada para {len(aplicadas)} associados ativos e aposentados.")
        return response  # Retorna a resposta padrão após o sucesso


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anuidades'] = AnuidadeModel.objects.order_by('-ano')
        return context
    
    
    
# View para editar anuidade
class EditAnuidadeView(UpdateView):
    model = AnuidadeModel
    form_class = AnuidadeForm
    template_name = 'app_finances/edit_anuidade.html'
    success_url = reverse_lazy('app_finances:create_anuidade')


# Financeiro Outras entradas e Despesas
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

        # Totasl de descontos anuidades
        total_descontos = DescontoAnuidade.objects.aggregate(total=Sum('valor_desconto'))['total'] or Decimal('0.00')
        
        # Totais financeiros gerais
        receita_total = AnuidadeAssociado.objects.aggregate(total_pago=Sum('valor_pago'))['total_pago'] or Decimal('0.00')
        saldo_pendente = AnuidadeAssociado.objects.aggregate(
            saldo_devedor=Sum('valor_pro_rata') - Sum('valor_pago')
        )['saldo_devedor'] or Decimal('0.00')

        # Total de pagantes = Associados Ativos + Associados Aposentados
        total_pagantes = AssociadoModel.objects.filter(
            status__in=["Associado Lista Ativo(a)", "Associado Lista Aposentado(a)"]
        ).count()

        context.update({
            "total_pagantes": total_pagantes,
        })
        # Associados em dia e em atraso
        associados_em_dia = AnuidadeAssociado.objects.filter(pago=True).values('associado').distinct().count()
        associados_em_atraso = total_pagantes - associados_em_dia

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
            'total_descontos': total_descontos,
            'saldo_pendente': saldo_pendente,
            'data_atual': data_atual,
            'associacoes_data': associacoes_data,
            'total_despesas': total_despesas,
            'total_pagantes': total_pagantes,

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
