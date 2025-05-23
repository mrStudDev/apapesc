from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Sum, Count, Q
from django.contrib import messages
from django.db import models
from decimal import Decimal
from django.utils.timezone import now
from datetime import datetime
from django.views.generic import DetailView, TemplateView, ListView, CreateView, UpdateView
from django.views import View
from django.db.models import Value, F
from django.db.models.functions import Concat, Lower, ExtractYear, ExtractMonth, TruncMonth
from django.contrib.auth.mixins import LoginRequiredMixin

# App Finances
from .models import (
    AnuidadeModel,
    AnuidadeAssociado,
    DescontoAnuidade,
    TipoDespesaModel,
    DespesaAssociacaoModel,
    EntradaFinanceira,
    Pagamento,
    TipoServicoModel,
    PagamentoEntrada,  # Added import for PagamentoEntrada
    EntradaAlteracaoModel,  # Added import for EntradaAlteracaoModel
)
# End App Finances ---------

from app_associados.models import AssociadoModel
from app_associacao.models import AssociacaoModel, ReparticoesModel


from .forms import (
    AnuidadeForm,
    DespesaAssociacaoForm,
    TipoDespesaForm,
    EntradaFinanceiraForm,
    TipoServicoForm,
    )

from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps
from django.contrib.messages.views import SuccessMessageMixin


# Lista de Anuidades
@login_required
def lista_anuidades(request):
    ano_selecionado = request.GET.get('ano')
    associacao_selecionada = request.GET.get('associacao')
    status_pagamento = request.GET.get('status') 

    anos_disponiveis = AnuidadeModel.objects.values_list('ano', flat=True).distinct().order_by('ano')
    associacoes = AssociacaoModel.objects.order_by('nome_fantasia')

    anuidades_associados = []

    if ano_selecionado:
        # Convertendo para inteiro para comparação
        ano_int = int(ano_selecionado)

        # Filtro inicial
        filtro = {
            'associado__data_filiacao__year__lte': ano_int,
            'anuidade__ano': ano_int,
        }

        if associacao_selecionada:
            filtro['associado__associacao_id'] = associacao_selecionada

        if status_pagamento == "pago":
            filtro['pago'] = True
        elif status_pagamento == "pendente":
            filtro['pago'] = False

        anuidades_associados = (
            AnuidadeAssociado.objects.filter(**filtro)
            .select_related('associado__user', 'associado__associacao', 'anuidade')
            .annotate(
                full_name=Concat(
                    F('associado__user__first_name'),
                    Value(' '),
                    F('associado__user__last_name')
                )
            )
            .order_by('full_name')
        )

        # Enriquecimento dos dados
        for anuidade_assoc in anuidades_associados:
            pagamentos_ano = anuidade_assoc.pagamentos.aggregate(
                total_pago=Sum('valor')
            )['total_pago'] or Decimal('0.00')
            anuidade_assoc.total_pago_ano = pagamentos_ano

            total_debito = (
                AnuidadeAssociado.objects.filter(
                    associado=anuidade_assoc.associado,
                    pago=False
                ).aggregate(
                    saldo_devedor=Sum(F('anuidade__valor_anuidade')) - Sum('valor_pago')
                )['saldo_devedor'] or Decimal('0.00')
            )
            anuidade_assoc.saldo_devedor_total = total_debito

    context = {
        'anos_disponiveis': anos_disponiveis,
        'ano_selecionado': ano_selecionado,
        'associacao_selecionada': associacao_selecionada,
        'status_selecionado': status_pagamento,
        'associacoes': associacoes,
        'anuidades_associados': anuidades_associados,
    }

    return render(request, 'app_finances/list_anuidades.html', context)


class FinanceiroAssociadoDetailView(LoginRequiredMixin ,DetailView):
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
            saldo = anuidade.anuidade.valor_anuidade - valor_pago - valor_desconto  # ✅ Agora usa o valor total da anuidade
            
            # ✅ Atualiza os totais corretamente
            total_anuidades += anuidade.anuidade.valor_anuidade  
            total_pago += valor_pago
            total_descontos += valor_desconto
            
            detalhes_anuidades.append({
                'ano': anuidade.anuidade.ano,
                'valor_total': anuidade.anuidade.valor_anuidade,  # ✅ Mostra o valor cheio da anuidade
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
        
        # Anuidades em aberto (saldo > 0) e de anos anteriores ao atual
        anuidades_em_aberto = [
            d for d in detalhes_anuidades
            if d['saldo'] > 0 and d['ano'] < datetime.now().year
        ]
        context['anuidades_em_aberto'] = anuidades_em_aberto
        context['exibir_botao_cobranca'] = bool(anuidades_em_aberto)  # True se houver
        
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
@login_required
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
        .order_by('user__first_name', 'user__last_name')  # 👈 ordenação alfabética
    )

    # Associados com anuidades do ano vigente em aberto
    associados_a_pagar = (
        AssociadoModel.objects.filter(
            anuidades_associados__anuidade__ano=ano_atual,
            anuidades_associados__pago=False
        )
        .annotate(
            valor_anuidade=Sum(F('anuidades_associados__anuidade__valor_anuidade'))  # ✅ Corrigido
        )
        .order_by('user__first_name', 'user__last_name')  # 👈 ordenação alfabética
    )

    # Associados com anuidades de anos anteriores em atraso
    associados_atrasados = (
        AssociadoModel.objects.filter(
            anuidades_associados__anuidade__ano__lt=ano_atual,
            anuidades_associados__pago=False
        )
        .annotate(
            valor_debito=Sum(F('anuidades_associados__anuidade__valor_anuidade')) - Sum('anuidades_associados__valor_pago')  # ✅ Corrigido
        )
        .order_by('user__first_name', 'user__last_name')  # 👈 ordenação alfabética
    )

    context = {
        'associados_em_dia': associados_em_dia,
        'associados_a_pagar': associados_a_pagar,
        'associados_atrasados': associados_atrasados,
        'ano_atual': ano_atual,
        'valor_anuidade_atual': valor_anuidade_atual,  # Adicionando o valor da anuidade ao contexto
    }

    return render(request, 'app_finances/tri_condictions.html', context)

@login_required
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

            # ✅ Sempre aplicar o valor TOTAL da anuidade
            AnuidadeAssociado.objects.create(
                anuidade=anuidade,
                associado=associado,
                valor_pago=0,  # Inicialmente não pago
                pago=False
            )
            aplicadas.append(anuidade.ano)

    if aplicadas:
        messages.success(request, f"Anuidade aplicada para os anos: {', '.join(map(str, aplicadas))}.")
    else:
        messages.error(request, "As anuidades já haviam sido aplicadas anteriormente.")

    # 🔄 Retorna para a mesma página do associado
    return redirect('app_associados:single_associado', pk=associado.id)



class CreateAnuidadeView(LoginRequiredMixin ,CreateView):
    model = AnuidadeModel
    form_class = AnuidadeForm
    template_name = 'app_finances/create_anuidade.html'
    success_url = reverse_lazy('app_finances:create_anuidade')

    def form_valid(self, form):
        anuidade = form.save(commit=False)  # Ainda não salva no banco

        # Modelos relacionados
        AssociadoModel = apps.get_model('app_associados', 'AssociadoModel')
        AnuidadeAssociado = apps.get_model('app_finances', 'AnuidadeAssociado')

        # ✅ Filtra apenas associados filiados no ano da anuidade
        associados_para_aplicar = AssociadoModel.objects.annotate(
            status_lower=Lower('status')
        ).filter(
            status_lower__in=['associado lista ativo(a)', 'associado lista aposentado(a)'],
            data_filiacao__isnull=False,
            data_filiacao__year__lte=anuidade.ano  # filiado até esse ano
        )

        # ⚠️ Validação: se ninguém está filiado no ano, bloqueia criação
        if not associados_para_aplicar.exists():
            messages.error(self.request, f"Nenhum associado estava filiado no ano {anuidade.ano}. A anuidade não foi criada.")
            return self.form_invalid(form)  # retorna erro

        # ✅ Agora sim salva no banco
        anuidade.save()

        aplicadas = []
        with transaction.atomic():
            for associado in associados_para_aplicar:
                if not AnuidadeAssociado.objects.filter(anuidade=anuidade, associado=associado).exists():
                    AnuidadeAssociado.objects.create(
                        anuidade=anuidade,
                        associado=associado,
                        valor_pago=Decimal('0.00'),
                        pago=False
                    )
                    aplicadas.append(associado.user.get_full_name() if associado.user else associado.id)

        messages.success(self.request, f"Anuidade {anuidade.ano} criada e aplicada para {len(aplicadas)} associado(s).")
        return super().form_valid(form)



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['anuidades'] = AnuidadeModel.objects.order_by('-ano')
        return context
    
    

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

            # 🔥 O desconto é tratado como um pagamento e reduz apenas o saldo
            anuidade_associado.valor_pago += valor_desconto  # Desconto age como uma baixa
            saldo_atual = anuidade_associado.calcular_saldo()

            # 🔄 Se o pagamento cobriu toda a anuidade, marcar como quitado
            if saldo_atual <= 0:
                anuidade_associado.pago = True  

            anuidade_associado.save()

            messages.success(request, f"Desconto de R$ {valor_desconto} aplicado com sucesso!")

    return redirect('app_finances:financeiro_associado', pk=anuidade_associado.associado.id)


# Lista de descontos - Página
class DescontosAnuidadesView(LoginRequiredMixin, TemplateView):
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


# View para editar anuidade
class EditAnuidadeView(LoginRequiredMixin, UpdateView):
    model = AnuidadeModel
    form_class = AnuidadeForm
    template_name = 'app_finances/edit_anuidade.html'
    success_url = reverse_lazy('app_finances:create_anuidade')
#======================================================================================



# ENTRADAS ==================================================================================

# ✅ View para criar uma nova entrada
class EntradaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = EntradaFinanceira
    form_class = EntradaFinanceiraForm
    template_name = 'app_finances/create_entradas.html'
    success_url = reverse_lazy('app_finances:edit_entrada')
    success_message = "Entrada registrada com sucesso!"

    def get_form_kwargs(self):
        """
        Passa o usuário logado e a associação selecionada para o formulário.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # ✅ Passa o usuário autenticado

        # 🔹 Obtém a associação selecionada via GET
        associacao_id = self.request.GET.get('associacao')
        if associacao_id:
            kwargs['associacao'] = get_object_or_404(AssociacaoModel, pk=associacao_id)

        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial.update({
            'associacao': self.request.GET.get('associacao'),
            'reparticao': self.request.GET.get('reparticao'),
            'tipo_servico': self.request.GET.get('tipo_servico'),
            'descricao': self.request.GET.get('descricao'),
        })
        return initial

    def form_valid(self, form):
        """Garante que a entrada será salva corretamente."""
        
        if not form.is_valid():
            messages.error(self.request, "Erro ao salvar! Verifique os dados informados.")
            return self.form_invalid(form)  

        # 🔥 Garante que `self.object` seja atribuído corretamente
        self.object = form.save(commit=False)  

        if self.object is None:  
            messages.error(self.request, "Erro interno ao salvar a entrada.")  
            return self.form_invalid(form)

        if not self.request.user.is_authenticated:
            messages.error(self.request, "Usuário não autenticado.")
            return self.form_invalid(form)

        # ✅ Define o usuário que criou a entrada
        self.object.criado_por = self.request.user
        self.object.save()  # 🔥 Agora `self.object` está definido corretamente
        
        servico_extra_id = self.request.GET.get('servico_extra_id')
        if servico_extra_id:
            from app_servicos.models import ServicoExtraAssociadoModel
            try:
                servico = ServicoExtraAssociadoModel.objects.get(id=servico_extra_id)
                servico.entrada_relacionada = self.object  # self.object é a entrada
                servico.save()
            except ServicoExtraAssociadoModel.DoesNotExist:
                pass

        messages.success(self.request, "Entrada registrada com sucesso!")
        return HttpResponseRedirect(reverse('app_finances:edit_entrada', args=[self.object.pk])) # 🔥 Redireciona corretamente


    def form_invalid(self, form):
        """
        Se o formulário for inválido, exibe os erros e mantém os dados.
        """
        messages.error(self.request, "Erro ao cadastrar entrada. Verifique os campos obrigatórios.")
        print("🔴 ERROS NO FORMULÁRIO:", form.errors)  # ✅ Exibe os erros no terminal para depuração
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['associacoes'] = AssociacaoModel.objects.all().order_by('nome_fantasia')
        context['reparticoes'] = ReparticoesModel.objects.none()

        # ✅ Se estiver criando a entrada a partir de um serviço extra
        servico_extra_id = self.request.GET.get('servico_extra_id')
        if servico_extra_id:
            from app_servicos.models import ServicoExtraAssociadoModel
            try:
                servico = ServicoExtraAssociadoModel.objects.get(pk=servico_extra_id)
                context['servico_relacionado'] = servico
            except ServicoExtraAssociadoModel.DoesNotExist:
                context['servico_relacionado'] = None

        return context



# Editar Entrada
class EntradaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = EntradaFinanceira
    form_class = EntradaFinanceiraForm
    template_name = 'app_finances/edit_entrada.html'
    success_message = "Entrada atualizada com sucesso!"

    def get_success_url(self):
        return reverse_lazy('app_finances:edit_entrada', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        """
        Passa o usuário logado para o formulário.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # ✅ Agora passa o usuário logado
        return kwargs

    def form_valid(self, form):
        """
        Atualiza a entrada financeira SOMENTE se houver alterações e redireciona corretamente.
        """
        entrada = form.instance  # Obtém a instância da entrada
        dados_atuais = {field: getattr(entrada, field) for field in form.changed_data}

        if not dados_atuais:
            print("⚠ [DEBUG] Nenhuma alteração detectada no formulário. Redirecionando sem salvar.")
            messages.info(self.request, "Nenhuma alteração foi feita.")
            return HttpResponseRedirect(self.get_success_url())  # 🔥 Redirecionamento correto

        entrada.criado_por = self.request.user  # 🔥 Atualiza o usuário que criou a entrad  a
        entrada.save()  # Salva somente se houve mudanças
        
        dados_anteriores = model_to_dict(entrada)
        self.registrar_alteracoes(entrada, dados_anteriores)

        messages.success(self.request, "Entrada atualizada com sucesso!")
        return HttpResponseRedirect(self.get_success_url())  # 🔥 Redirecionamento correto

    def registrar_alteracoes(self, entrada, dados_anteriores):
        """
        Compara os valores antigos e novos e registra no histórico de alterações,
        garantindo que associações, repartições e tipo de serviço usem nomes ao invés de IDs.
        """
        dados_atualizados = model_to_dict(entrada)  # Obtém os novos valores

        campos_relevantes = [
            'associacao', 'reparticao', 'tipo_servico', 
            'descricao', 'valor_total', 'forma_pagamento', 'parcelamento', 'status_pagamento'
        ]

        for campo in campos_relevantes:
            valor_antigo = dados_anteriores.get(campo, None)
            valor_novo = dados_atualizados.get(campo, None)

            # 🔹 Trata FK para exibir o nome e não o ID
            if campo == "associacao" and valor_antigo:
                valor_antigo = AssociacaoModel.objects.filter(id=valor_antigo).first()
                valor_antigo = valor_antigo.nome_fantasia if valor_antigo else "Nenhuma"
                valor_novo = entrada.associacao.nome_fantasia if entrada.associacao else "Nenhuma"

            elif campo == "reparticao" and valor_antigo:
                valor_antigo = ReparticoesModel.objects.filter(id=valor_antigo).first()
                valor_antigo = valor_antigo.nome_reparticao if valor_antigo else "Nenhuma"
                valor_novo = entrada.reparticao.nome_reparticao if entrada.reparticao else "Nenhuma"

            elif campo == "tipo_servico" and valor_antigo:
                valor_antigo = TipoServicoModel.objects.filter(id=valor_antigo).first()
                valor_antigo = valor_antigo.nome if valor_antigo else "Nenhum"
                valor_novo = entrada.tipo_servico.nome if entrada.tipo_servico else "Nenhum"

            # 🔹 Trata Choices (Parcelamento e Forma de Pagamento)
            elif campo == "parcelamento":
                valor_antigo = dict(EntradaFinanceira.PARCELAMENTO_CHOICES).get(valor_antigo, valor_antigo)
                valor_novo = dict(EntradaFinanceira.PARCELAMENTO_CHOICES).get(valor_novo, valor_novo)

            elif campo == "forma_pagamento":
                valor_antigo = dict(EntradaFinanceira.FORMA_PAGAMENTO_CHOICES).get(valor_antigo, valor_antigo)
                valor_novo = dict(EntradaFinanceira.FORMA_PAGAMENTO_CHOICES).get(valor_novo, valor_novo)

            # 🔥 Só grava se houver mudança real
            if str(valor_antigo) != str(valor_novo):
                EntradaAlteracaoModel.objects.create(
                    entrada=entrada,
                    campo_alterado=campo.replace("_", " ").capitalize(),
                    valor_anterior=valor_antigo,
                    valor_novo=valor_novo,
                    alterado_por=self.request.user
                )

    def get_context_data(self, **kwargs):
        """
        Adiciona associações, repartições e status de pagamento ao contexto.
        """
        context = super().get_context_data(**kwargs)
        entrada = self.object  # A entrada que está sendo editada
        valor_ainda_devido = entrada.valor_total - entrada.valor_pagamento
        # 🔹 Pega pagamentos da entrada
        pagamentos = entrada.pagamentos.all().order_by("-data_pagamento")
        alteracoes = entrada.alteracoes.all().order_by("-data_alteracao")
        # 🔹 Atualizamos o contexto
        context['exibir_botao_recibo'] = entrada.status_pagamento == 'pago' and hasattr(entrada, 'entrada_servico_extra') and entrada.entrada_servico_extra.extra_associado
        
        context.update({
            'entrada': entrada,
            'associacoes': AssociacaoModel.objects.all(),
            'reparticoes': ReparticoesModel.objects.all(),
            "valor_ainda_devido": valor_ainda_devido,
            "pagamentos": entrada.pagamentos.all().order_by("-data_pagamento"),
            "alteracoes": entrada.alteracoes.all().order_by("-data_alteracao"),
        })
        return context



from decimal import Decimal, InvalidOperation
import json

@login_required
def registrar_pagamento(request, entrada_id):
    entrada = get_object_or_404(EntradaFinanceira, id=entrada_id)

    if request.method == "POST":
        valor_pago = request.POST.get("valor_pago")

        # 🔹 Se `valor_pago` for None ou string vazia, define como "0.00"
        if not valor_pago:
            valor_pago = "0.00"

        try:
            # 🔹 Garante que é um Decimal válido
            valor_pago = Decimal(str(valor_pago).replace(",", "."))
        except (InvalidOperation, AttributeError, ValueError):
            messages.error(request, "Valor inválido. Digite um número válido.")
            return redirect("app_finances:edit_entrada", pk=entrada.id)

        # 🔹 Valida se o pagamento não ultrapassa o devido
        saldo_restante = entrada.valor_total - entrada.valor_pagamento
        if valor_pago > saldo_restante:
            messages.error(request, f"Erro: Você não pode pagar mais do que o valor restante (R$ {saldo_restante:.2f}).")
            return redirect("app_finances:edit_entrada", pk=entrada.id)

        # 🔹 Registra o pagamento
        pagamento = PagamentoEntrada.objects.create(
            entrada=entrada,
            valor_pago=valor_pago,
            data_pagamento=now(),
            registrado_por=request.user
        )

        # 🔹 Atualiza o valor já pago e recalcula status
        entrada.calcular_pagamento()

        messages.success(request, f"Pagamento de R$ {valor_pago:.2f} registrado com sucesso!")
        return redirect("app_finances:edit_entrada", pk=entrada.id)



# Tipo de Servições - Entradas
class TipoServicoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = TipoServicoModel
    form_class = TipoServicoForm
    template_name = 'app_finances/create_tipo_servico.html'
    success_url = reverse_lazy('app_finances:create_tipo_servico')  # Redireciona para lista de entradas
    success_message = "Tipo de Serviço cadastrado com sucesso!"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tipos_servicos"] = TipoServicoModel.objects.all().order_by('nome')
        return context
    
class EditTipoServicoView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = TipoServicoModel
    form_class = TipoServicoForm
    template_name = 'app_finances/edit_tipo_servico.html'
    success_url = reverse_lazy('app_finances:create_tipo_servico')  # Redireciona para o listagem/cadastro
    success_message = "Tipo de Serviço atualizado com sucesso!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tipos_servicos"] = TipoServicoModel.objects.all().order_by('nome')
        return context
    
class ListEntradasView(LoginRequiredMixin, ListView):
    model = EntradaFinanceira
    template_name = 'app_finances/list_entradas.html'
    context_object_name = 'entradas'
    paginate_by = 1000  # 🔹 Paginação com 1000 registros por página

    def get_queryset(self):
        """
        Filtra as entradas com base nos parâmetros da URL (associação, repartição, ano e mês).
        """
        queryset = EntradaFinanceira.objects.select_related('associacao', 'reparticao', 'tipo_servico')

        # 🔹 Obtendo os filtros da URL
        associacao_id = self.request.GET.get('associacao')
        reparticao_id = self.request.GET.get('reparticao')
        ano = self.request.GET.get('ano')
        mes = self.request.GET.get('mes')

        # 🔹 Aplica filtros somente se valores forem fornecidos
        if associacao_id:
            queryset = queryset.filter(associacao_id=associacao_id)

        if reparticao_id:
            queryset = queryset.filter(reparticao_id=reparticao_id)

        if ano:
            queryset = queryset.filter(data_criacao__year=ano)  # ✅ Agora filtra pelo ano corretamente

        if mes:
            queryset = queryset.filter(data_criacao__month=mes)  # ✅ Agora filtra pelo mês corretamente

        return queryset.order_by('-data_criacao')  # 🔹 Mais recentes primeiro

    def get_context_data(self, **kwargs):
        """
        Adiciona listas de associações, repartições, anos e meses ao contexto para os filtros.
        """
        context = super().get_context_data(**kwargs)
        context['associacoes'] = AssociacaoModel.objects.all()
        context['reparticoes'] = ReparticoesModel.objects.all()
        context['anos'] = EntradaFinanceira.objects.dates('data_criacao', 'year', order='DESC')
        context['meses'] = range(1, 13)  # 🔹 Lista de meses de 1 a 12

        # 🔹 Mantém os valores selecionados nos filtros para evitar reset após pesquisa
        context['associacao_selecionada'] = self.request.GET.get('associacao', '')
        context['reparticao_selecionada'] = self.request.GET.get('reparticao', '')
        context['ano_selecionado'] = self.request.GET.get('ano', now().year)
        context['mes_selecionado'] = self.request.GET.get('mes', '')

        return context



# DESPESAS
class DespesaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = DespesaAssociacaoModel
    form_class = DespesaAssociacaoForm
    template_name = 'app_finances/create_despesa.html'
    success_url = reverse_lazy('app_finances:list_despesas')
    success_message = "Despesa lançada com sucesso!"

    def get_form_kwargs(self):
        """
        Passa o usuário logado e a associação selecionada para o formulário.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Passa o usuário logado para o formulário

        # Obtém a associação selecionada, se houver
        associacao_id = self.request.GET.get('associacao')
        if associacao_id:
            kwargs['associacao'] = get_object_or_404(AssociacaoModel, pk=associacao_id)

        return kwargs

    def get_context_data(self, **kwargs):
        """
        Adiciona as associações e repartições ao contexto.
        """
        context = super().get_context_data(**kwargs)
        context['associacoes'] = AssociacaoModel.objects.all().order_by('nome_fantasia')
        context['reparticoes'] = ReparticoesModel.objects.none()  # Inicialmente, nenhuma repartição
        context['tipos_despesas'] = TipoDespesaModel.objects.all().order_by('nome') 
        return context
    
    def form_valid(self, form):
        """Define o usuário que registrou a despesa e redireciona conforme a escolha do usuário."""
        self.object = form.save(commit=False)
        self.object.registrado_por = self.request.user  
        self.object.save()  

        form.save_m2m()  # Se houver m2m (padrão)

        # Garante que o comprovante seja salvo
        if 'comprovante_nota' in form.cleaned_data:
            self.object.comprovante_nota = form.cleaned_data['comprovante_nota']
            self.object.save()

        # 🔥 Captura a ação desejada pelo usuário
        acao = self.request.POST.get("acao")

        if acao == "salvar_editar":
            return redirect('app_finances:edit_despesa', pk=self.object.pk)  # Redireciona para edição

        if acao == "salvar_nova":
            return redirect('app_finances:create_despesa')  # Redireciona para novo cadastro

        return super().form_valid(form) # Redireciona para novo cadastro


# Editar Despesa
class DespesaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = DespesaAssociacaoModel
    form_class = DespesaAssociacaoForm
    template_name = 'app_finances/edit_despesa.html'
    success_url = reverse_lazy('app_finances:list_despesas')
    success_message = "Despesa atualizada com sucesso!"

    def get_form_kwargs(self):
        """
        Passa o usuário logado para o formulário.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # ✅ Agora passa o usuário logado
        return kwargs
    
    def form_valid(self, form):
        """
        Garante que a alteração será salva com o usuário correto.
        """
        despesa = form.save(commit=False)  # ✅ Não salva ainda
        despesa.save(usuario_atualizacao=self.request.user)  # ✅ Passa o usuário logado corretamente
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Adiciona associações e repartições ao contexto.
        """
        context = super().get_context_data(**kwargs)
        context['despesa'] = self.object  # Adiciona a despesa específica
        context['associacoes'] = AssociacaoModel.objects.all()
        context['reparticoes'] = ReparticoesModel.objects.all()
        return context

 # Carregar dados Repartições para Filtro Despesas e Entradas
def carregar_reparticoes(request):
    associacao_id = request.GET.get('associacao_id')
    if associacao_id:
        reparticoes = ReparticoesModel.objects.filter(associacao_id=associacao_id).values('id', 'nome_reparticao')
        return JsonResponse(list(reparticoes), safe=False)
    else:
        return JsonResponse([], safe=False)  # Retorna uma lista vazia se não houver associacao_id


# Tipo Despesa
class TipoDespesaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = TipoDespesaModel
    form_class = TipoDespesaForm
    template_name = 'app_finances/create_tipo_despesa.html'
    success_url = reverse_lazy('app_finances:create_tipo_despesa')
    success_message = "Tipo de Despesa criado com sucesso!"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos_despesas'] = TipoDespesaModel.objects.all().order_by('nome')  # Adiciona tipos de despesas
        return context


# Despesas - LISTAS
class ListDespesasView(LoginRequiredMixin, ListView):
    model = DespesaAssociacaoModel
    template_name = 'app_finances/list_despesas.html'
    context_object_name = 'despesas'
    paginate_by = 1000  # Exibe 1000 egistros por página

    def get_queryset(self):
        """
        Filtra as despesas com base nos parâmetros da URL (associação, repartição, mês e ano).
        """
        queryset = DespesaAssociacaoModel.objects.all().select_related('associacao', 'reparticao', 'tipo_despesa')

        # 🔥 Filtros opcionais
        associacao_id = self.request.GET.get('associacao')
        reparticao_id = self.request.GET.get('reparticao')
        tipo_despesa_id = self.request.GET.get('tipo_despesa')
        mes = self.request.GET.get('mes')
        ano = self.request.GET.get('ano')

        # Filtro por Associação
        if associacao_id:
            queryset = queryset.filter(associacao_id=associacao_id)

        # Filtro por Repartição (se houver)
        if reparticao_id:
            queryset = queryset.filter(reparticao_id=reparticao_id)
            
        # Filtro por Tipo de Despesa (se houver)
        if tipo_despesa_id:
            queryset = queryset.filter(tipo_despesa_id=tipo_despesa_id)  # 👈 Filtro adicionado aqui

        # Filtro por Ano
        if ano:
            queryset = queryset.filter(data_lancamento__year=ano)

        # Filtro por Mês
        if mes:
            queryset = queryset.filter(data_lancamento__month=mes)

        # Ordenação das despesas (mais recentes primeiro)
        queryset = queryset.order_by('-data_lancamento')

        return queryset

    def get_context_data(self, **kwargs):
        """
        Adiciona listas de associações, repartições, anos e meses ao contexto para os filtros.
        """
        context = super().get_context_data(**kwargs)
        context['associacoes'] = AssociacaoModel.objects.all()
        context['reparticoes'] = ReparticoesModel.objects.all()
        context['tipos_despesa'] = TipoDespesaModel.objects.all() 
        context['anos'] = DespesaAssociacaoModel.objects.dates('data_lancamento', 'year', order='DESC')
        context['meses'] = range(1, 13)  # Lista de meses de 1 a 12

        # Valores selecionados nos filtros (para manter após pesquisa)
        context['associacao_selecionada'] = self.request.GET.get('associacao', '')
        context['reparticao_selecionada'] = self.request.GET.get('reparticao', '')
        context['ano_selecionado'] = self.request.GET.get('ano', now().year)
        context['mes_selecionado'] = self.request.GET.get('mes', '')

        return context


# SUPER FIANCEIRO
# Financeiro Outras entradas e Despesas
class ResumoFinanceiroView(LoginRequiredMixin, TemplateView):
    template_name = 'app_finances/finances_super.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Data atual
        data_atual = timezone.now().date()

        # Total geral de associados
        total_associados = AssociadoModel.objects.count()
        
        # 🔹 Total Geral das Anuidades Apuradas (Somente associados ativos e aposentados)
        total_anuidades_apuradas = AnuidadeAssociado.objects.filter(
            associado__status__in=["Associado Lista Ativo(a)", "Associado Lista Aposentado(a)", "Desassociado(a)"]
        ).aggregate(total=Sum('anuidade__valor_anuidade'))['total'] or Decimal('0.00')

        # Resumo geral de despesas
        total_despesas = DespesaAssociacaoModel.objects.aggregate(total=Sum('valor'))['total'] or 0

        # Totasl de descontos anuidades
        total_descontos = DescontoAnuidade.objects.aggregate(total=Sum('valor_desconto'))['total'] or Decimal('0.00')
        
        # Totais financeiros gerais
        receita_total = AnuidadeAssociado.objects.aggregate(total_pago=Sum('valor_pago'))['total_pago'] or Decimal('0.00')
        # Descontos
        total_descontos = DescontoAnuidade.objects.aggregate(total=Sum('valor_desconto'))['total'] or Decimal('0.00')
        # ✅ Receita apurada real = valor pago - descontos
        realmente_apuradas = receita_total - total_descontos
        saldo_pendente = AnuidadeAssociado.objects.aggregate(
            saldo_devedor=Sum(F('anuidade__valor_anuidade') - F('valor_pago'))
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
                saldo_pendente=Sum(F('anuidade__valor_anuidade')) - Sum('valor_pago')
            )['saldo_pendente'] or Decimal('0.00')

            associacoes_data.append({
                'nome': associacao.nome_fantasia,
                'total_associados': total_associados_assoc,
                'receita_total': receita_assoc,
                'saldo_pendente': saldo_assoc,
            })
            
       # 🔹 Filtra associados ativos e aposentados
        associados = AssociadoModel.objects.filter(
            status__in=["Associado Lista Ativo(a)", "Associado Lista Aposentado(a)"]
        )


       # 🔹 Total geral de despesas
        total_despesas = DespesaAssociacaoModel.objects.aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

        # 🔹 Total Pago (Somente despesas pagas)
        total_pagas = DespesaAssociacaoModel.objects.filter(pago=True).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0.00')

        # 🔹 Total a Pagar (Despesas que ainda NÃO foram pagas)
        total_a_pagar = DespesaAssociacaoModel.objects.filter(pago=False).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0.00')

        # 🔹 Total Vencidas (Despesas pendentes cuja data de vencimento já passou)
        total_vencidas = DespesaAssociacaoModel.objects.filter(
            pago=False, data_vencimento__lt=data_atual
        ).aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0.00')

        # 🔥 🔹 Despesas agrupadas por Associação
        despesas_por_associacao = DespesaAssociacaoModel.objects.values(
            'associacao__nome_fantasia'
        ).annotate(
            total_despesas=Sum('valor')
        ).order_by('associacao__nome_fantasia')

        # 🔥 🔹 Despesas agrupadas por Repartição dentro de cada Associação
        despesas_por_reparticao = DespesaAssociacaoModel.objects.values(
            'associacao__nome_fantasia',
            'reparticao__nome_reparticao'
        ).annotate(
            total_despesas=Sum('valor')
        ).order_by('associacao__nome_fantasia', 'reparticao__nome_reparticao')

        # 🔥 🔹 Organizando os dados de despesas
        associacoes_com_reparticoes = {}

        for despesa in despesas_por_associacao:
            associacao_nome = despesa["associacao__nome_fantasia"]
            associacoes_com_reparticoes[associacao_nome] = {
                "total_despesas": despesa["total_despesas"],
                "reparticoes": []
            }

        for despesa in despesas_por_reparticao:
            associacao_nome = despesa["associacao__nome_fantasia"]
            reparticao_nome = despesa["reparticao__nome_reparticao"] or "Sem Repartição"

            if associacao_nome in associacoes_com_reparticoes:
                associacoes_com_reparticoes[associacao_nome]["reparticoes"].append({
                    "reparticao_nome": reparticao_nome,
                    "total_despesas": despesa["total_despesas"]
                })

        # 🔹 Total Geral de Entradas (Receitas)
        total_entradas = EntradaFinanceira.objects.aggregate(total=Sum('valor_total'))['total'] or Decimal('0.00')

        # 🔹 Total Já Recebido
        total_recebido = EntradaFinanceira.objects.aggregate(total=Sum('valor_pagamento'))['total'] or Decimal('0.00')

        # 🔹 Total a Receber (Falta ser pago)
        total_a_receber = total_entradas - total_recebido

        # 🔹 Total Atrasado (Entradas vencidas e pendentes)
        total_atrasado = EntradaFinanceira.objects.filter(
            status_pagamento__in=["pendente", "parcial"], data_criacao__lt=data_atual
        ).aggregate(total=Sum(F("valor_total") - F("valor_pagamento")))['total'] or Decimal('0.00')

        # 🔥 🔹 Entradas agrupadas por Associação
        entradas_por_associacao = EntradaFinanceira.objects.values(
            'associacao__nome_fantasia'
        ).annotate(
            total_receita=Sum('valor_total'),
            total_recebido=Sum('valor_pagamento')
        ).order_by('associacao__nome_fantasia')

        # 🔥 🔹 Entradas agrupadas por Repartição dentro de cada Associação
        entradas_por_reparticao = EntradaFinanceira.objects.values(
            'associacao__nome_fantasia',
            'reparticao__nome_reparticao'
        ).annotate(
            total_receita=Sum('valor_total'),
            total_recebido=Sum('valor_pagamento')
        ).order_by('associacao__nome_fantasia', 'reparticao__nome_reparticao')

        # 🔥 🔹 Organizando os dados de receitas
        associacoes_com_reparticoes_receitas = {}

        for entrada in entradas_por_associacao:
            associacao_nome = entrada["associacao__nome_fantasia"]
            associacoes_com_reparticoes_receitas[associacao_nome] = {
                "total_receita": entrada["total_receita"],
                "total_recebido": entrada["total_recebido"],
                "reparticoes": []
            }

        for entrada in entradas_por_reparticao:
            associacao_nome = entrada["associacao__nome_fantasia"]
            reparticao_nome = entrada["reparticao__nome_reparticao"] or "Sem Repartição"

            if associacao_nome in associacoes_com_reparticoes_receitas:
                associacoes_com_reparticoes_receitas[associacao_nome]["reparticoes"].append({
                    "reparticao_nome": reparticao_nome,
                    "total_receita": entrada["total_receita"],
                    "total_recebido": entrada["total_recebido"]
                })
                
        # 🔹 Total de Despesas Pagas
        total_despesas_pagas = DespesaAssociacaoModel.objects.filter(pago=True).aggregate(
            total=Sum('valor'))['total'] or Decimal('0.00')
                        
        # 🔹 Total de Despesas Pendentes
        total_despesas_pendentes = total_despesas - total_despesas_pagas

        # 🔹 Saldo Atual (Total Recebido - Despesas Pagas)
        saldo_atual = total_recebido + realmente_apuradas- total_despesas_pagas

        # 🔹 Saldo Projetado (Se todas as receitas e despesas forem quitadas)
        saldo_projetado = (saldo_pendente + total_a_receber) - total_despesas

        # 🔹 Valores a Receber
        total_a_receber = total_entradas - total_recebido
        total_anuidades_pendentes = total_anuidades_apuradas - total_recebido

        # 🔹 Valores a Pagar
        total_entradas_geral = total_entradas + total_anuidades_apuradas
        total_despesas_geral = total_despesas + total_descontos
        saldo_geral = total_entradas_geral - total_despesas_geral
        
        # 🔹 Contagem de associados por categoria
        associados_ativos = AssociadoModel.objects.filter(status="Associado Lista Ativo(a)").count()
        associados_aposentados = AssociadoModel.objects.filter(status="Associado Lista Aposentado(a)").count()
        associados_especiais = AssociadoModel.objects.filter(status="Cliente Especial").count()
        total_candidatos = AssociadoModel.objects.filter(status="Candidato(a)").count()
        total_desassociados = AssociadoModel.objects.filter(status="Desassociado(a)").count()

        # 🔹 Graficos
        # ✅ Novo: entradas = receita_real_anuidades + receitas de entradas extras
        entrada_real_total = float(realmente_apuradas + total_recebido)  # <- soma das duas origens

        despesa_total = float(total_pagas)

        context["grafico_comparativo_financeiro"] = json.dumps({
            "entrada_real": round(entrada_real_total, 2),
            "despesa": round(despesa_total, 2)
        })
        
        entradas_por_mes = (
            EntradaFinanceira.objects
            .annotate(mes=TruncMonth('data_criacao'))
            .values('mes')
            .annotate(valor=Sum('valor_pagamento'))
            .order_by('mes')
        )

        meses_entradas = [d['mes'].strftime('%Y-%m') for d in entradas_por_mes]
        valores_entradas = [float(d['valor']) for d in entradas_por_mes]
        # 🔹 Gráficos de receitas e despesas por associação
        context["grafico_associacoes_labels"] = json.dumps([a["nome"] for a in associacoes_data])
        context["grafico_associacoes_receitas"] = json.dumps([float(a["receita_total"]) for a in associacoes_data])
        context["grafico_associacoes_saldos"] = json.dumps([float(a["saldo_pendente"]) for a in associacoes_data])
        # Total sem desconto (para o gráfico de comparação)
        
        #total_sem_desconto = total_anuidades_apuradas - total_descontos
        total_sem_desconto = total_anuidades_apuradas - receita_total
        # 🔹 Gráfico: Pagas x Em Atraso
        context["grafico_anuidades_pagamento"] = json.dumps([
            associados_em_dia,
            associados_em_atraso
        ])

        # 🔹 Gráfico: Valores Pagos x Pendentes
        context["grafico_valores_anuidades"] = json.dumps([
            float(receita_total),
            float(saldo_pendente)
        ])

        # 🔹 Gráfico: Descontos x Sem Desconto
        total_sem_desconto = float(total_anuidades_apuradas) - float(total_descontos)
        context["grafico_descontos_anuidades"] = json.dumps([
            float(total_descontos),
            total_sem_desconto
        ])
        
        # 🔹 Receita total = tudo que entrou via anuidades (valor já pago)
        receita_total = AnuidadeAssociado.objects.aggregate(
            total_pago=Sum('valor_pago')
        )['total_pago'] or Decimal('0.00')

        # 🔹 Total de descontos concedidos (somente registros oficiais)
        total_descontos = DescontoAnuidade.objects.aggregate(
            total=Sum('valor_desconto')
        )['total'] or Decimal('0.00')

        # 🔹 Receita realmente apurada = o que entrou de fato após descontos
        realmente_apuradas = receita_total - total_descontos

        
        # Adicionar informações ao contexto
        context.update({
            "total_associados": total_associados,
            "associados_ativos": associados_ativos,
            "associados_aposentados": associados_aposentados,
            "associados_especiais": associados_especiais,
            "total_candidatos": total_candidatos,
            "total_desassociados": total_desassociados,
            
            # Associados e Anuidades
            'total_associados': total_associados,
            'associados_em_dia': associados_em_dia,
            'associados_em_atraso': associados_em_atraso,
            'receita_total': receita_total,
            'total_descontos': total_descontos,
            'saldo_pendente': saldo_pendente,
            'data_atual': data_atual,
            'associacoes_data': associacoes_data,
            'total_pagantes': total_pagantes,
            'total_anuidades_apuradas': total_anuidades_apuradas, # Total Global Lançamentos de Anuidades
            "realmente_apuradas": realmente_apuradas,

            
            # Despesas
            'total_despesas': total_despesas,
            "total_pagas": total_pagas,
            "total_a_pagar": total_a_pagar,
            "total_vencidas": total_vencidas, 
            'despesas_por_associacao': despesas_por_associacao,
            'despesas_por_reparticao': despesas_por_reparticao,  # ✅ Adicionando ao contexto
            'associacoes_com_reparticoes': associacoes_com_reparticoes,  # ✅ Despesas Total
            
            # Entradas
            "total_entradas": total_entradas,
            "total_recebido": total_recebido,
            "total_a_receber": total_a_receber,
            "total_atrasado": total_atrasado,
             "associacoes_com_reparticoes_receitas": associacoes_com_reparticoes_receitas,  # ✅ Receitas
             
            # Resumo Resumo Financeiro
            'total_despesas_pagas': total_despesas_pagas,
            'total_despesas_pendentes': total_despesas_pendentes,
            'saldo_atual': saldo_atual,
            'saldo_projetado': saldo_projetado,
            'total_a_receber': total_a_receber,
            'total_anuidades_pendentes': total_anuidades_pendentes,
            'total_entradas_geral': total_entradas_geral,
            'total_despesas_geral': total_despesas_geral,
            'saldo_geral': saldo_geral,
            
            # Gráficos
            'meses_entradas': json.dumps(meses_entradas),
            'valores_entradas': json.dumps(valores_entradas)
            
        })

        return context
    
# Relatórios ===============================

# Pagamentos Anuidades ===
class RelatorioAnuidadesView(LoginRequiredMixin, TemplateView):
    template_name = 'app_finances/relatorio_anuidades.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 🔎 Captura os filtros
        nome_query = self.request.GET.get('q', '').strip()
        associacao_filtro = self.request.GET.get('associacao', '')
        reparticao_filtro = self.request.GET.get('reparticao', '')
        ano_filtro = self.request.GET.get('ano', '')

        pagamentos = Pagamento.objects.select_related(
            'anuidade_associado__associado__associacao',
            'anuidade_associado__associado__reparticao',
            'anuidade_associado__anuidade',
            'registrado_por'
        )

        # 🔤 Filtro por nome
        if nome_query:
            pagamentos = pagamentos.filter(
                Q(anuidade_associado__associado__user__first_name__icontains=nome_query) |
                Q(anuidade_associado__associado__user__last_name__icontains=nome_query)
            )

        # 🏢 Filtro por associação
        if associacao_filtro:
            pagamentos = pagamentos.filter(anuidade_associado__associado__associacao__id=associacao_filtro)

        # 🏬 Filtro por repartição
        if reparticao_filtro:
            pagamentos = pagamentos.filter(anuidade_associado__associado__reparticao__id=reparticao_filtro)

        # 📅 Filtro por ano
        if ano_filtro:
            pagamentos = pagamentos.filter(anuidade_associado__anuidade__ano=ano_filtro)

        pagamentos = pagamentos.order_by(
            'anuidade_associado__associado__associacao__nome_fantasia',
            'anuidade_associado__associado__reparticao__nome_reparticao',
            'anuidade_associado__associado__user__first_name',
            'anuidade_associado__anuidade__ano'
        )

        relatorio = []
        for pagamento in pagamentos:
            associado = pagamento.anuidade_associado.associado
            associacao = associado.associacao
            reparticao = associado.reparticao

            relatorio.append({
                'associacao': associacao.nome_fantasia if associacao else "Sem Associação",
                'reparticao': reparticao.nome_reparticao if reparticao else "Sem Repartição",
                'associado_nome': associado.user.get_full_name(),
                'associado_id': associado.id,  # 👈 ESSENCIAL
                'associado_cpf': associado.cpf,
                'ano_anuidade': pagamento.anuidade_associado.anuidade.ano,
                'valor_pago': pagamento.valor,
                'data_pagamento': pagamento.data_pagamento,
                'registrado_por': pagamento.registrado_por.get_full_name() if pagamento.registrado_por else "N/A"
            })

        context.update({
            'relatorio': relatorio,
            'data_hoje': now().strftime('%d/%m/%Y'),
            'associacoes': AssociacaoModel.objects.all(),
            'reparticoes': ReparticoesModel.objects.all(),
            'anos': AnuidadeModel.objects.values_list('ano', flat=True).distinct().order_by('-ano'),
            'nome_query': nome_query,
            'associacao_filtro': associacao_filtro,
            'reparticao_filtro': reparticao_filtro,
            'ano_filtro': ano_filtro,
        })

        return context
