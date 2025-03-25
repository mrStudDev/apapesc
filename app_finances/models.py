from django.shortcuts import render
from django.contrib.auth.models import User 
from django.db import models, transaction
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
from app_associados.models import AssociadoModel, AssociacaoModel
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum, Q
from django.apps import apps 
from django.conf import settings
from django.db.models.functions import Lower
from django.forms.models import model_to_dict
from datetime import datetime

class AnuidadeModel(models.Model):
    ano = models.PositiveIntegerField(unique=True, verbose_name="Ano da Anuidade")
    valor_anuidade = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor da Anuidade")
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-ano']
        verbose_name = "Anuidade"
        verbose_name_plural = "Anuidades"

    def __str__(self):
        return f"Anuidade {self.ano} - R$ {self.valor_anuidade}"

    def save(self, *args, **kwargs):
        """
        Ao salvar a anuidade, atribuir a todos os associados existentes.
        """
        super().save(*args, **kwargs)
        self.atribuir_anuidades_associados()


    def atribuir_anuidades_associados(self):
        """
        Atribui esta anuidade apenas aos associados ATIVOS e APOSENTADOS,
        garantindo que o filtro funcione corretamente.
        """
        # Evita import circular com app_associados
        AssociadoModel = apps.get_model('app_associados', 'AssociadoModel')
        AnuidadeAssociado = apps.get_model('app_finances', 'AnuidadeAssociado')

        # 🔥 🚀 Filtra APENAS os associados ATIVOS e APOSENTADOS 🚀 🔥
        associados = AssociadoModel.objects.annotate(
            status_lower=Lower('status')
        ).filter(
            status_lower__in=['associado lista ativo(a)', 'associado lista aposentado(a)']
        )

        print(f"✅ Associados válidos encontrados: {associados.count()}")  # DEBUG

        with transaction.atomic():
            for associado in associados:
                if not AnuidadeAssociado.objects.filter(anuidade=self, associado=associado).exists():
                    # ✅ Aplica o valor TOTAL da anuidade, sem cálculo pró-rata
                    AnuidadeAssociado.objects.create(
                        anuidade=self,
                        associado=associado,
                        valor_pago=Decimal('0.00'),
                        pago=False
                    ) 
                    

    def calcular_meses_validos(self, associado):
        """
        Calcula o número de meses para o cálculo pró-rata
        com base em associado.data_filiacao e self.ano.
        """
        if not associado.data_filiacao or associado.data_filiacao.year > self.ano:
            print(f"⚠️ Nenhum mês válido para {associado} - Data de Filiação: {associado.data_filiacao}, Anuidade: {self.ano}")
            return 0

        if associado.data_filiacao.year == self.ano:
            meses = 12 - associado.data_filiacao.month + 1
            print(f"✅ Cálculo pró-rata para {associado}: {meses} meses")  # DEBUG
            return meses
        
        print(f"✅ Anuidade completa para {associado}")
        return 12  # Se a filiação foi antes do ano da anuidade, paga o valor total


class AnuidadeAssociado(models.Model):
    anuidade = models.ForeignKey(AnuidadeModel, on_delete=models.CASCADE, related_name='anuidades_associados')
    associado = models.ForeignKey(
        'app_associados.AssociadoModel',
        on_delete=models.CASCADE,
        related_name='anuidades_associados'
    )
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Valor Pago")
    pago = models.BooleanField(default=False, verbose_name="Anuidade Paga")
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('anuidade', 'associado')
        ordering = ['associado']
        verbose_name = "Anuidade do Associado"
        verbose_name_plural = "Anuidades dos Associados"

    def __str__(self):
        return f"Anuidade {self.anuidade.ano} - {self.associado}"

    def calcular_saldo(self):
        """Calcula o saldo devedor da anuidade."""
        return max(self.anuidade.valor_anuidade - self.valor_pago, Decimal('0.00'))  # ✅ Agora acessamos `valor_anuidade` corretamente


    def dar_baixa(self, valor_baixa):
        """Dá baixa parcial ou total no valor da anuidade."""
        self.valor_pago += valor_baixa
        if self.valor_pago >= self.anuidade.valor_anuidade:  # ✅ Comparação com o valor cheio da anuidade
            self.pago = True
        self.save()

# Pagamento de uma Anuidade
class Pagamento(models.Model):
    anuidade_associado = models.ForeignKey(AnuidadeAssociado, on_delete=models.CASCADE, related_name='pagamentos', default=None)
    data_pagamento = models.DateField(auto_now_add=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Pago")
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Registrado por")

    def __str__(self):
        return f"Pagamento de R$ {self.valor} em {self.data_pagamento}"
    
    
class DescontoAnuidade(models.Model):
    anuidade_associado = models.ForeignKey(
        AnuidadeAssociado,
        on_delete=models.CASCADE,
        related_name="descontos",
        verbose_name="Anuidade Associado"
    )
    valor_desconto = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Valor do Desconto"
    )
    motivo = models.TextField(verbose_name="Motivo do Desconto")
    concedido_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Concedido por"
    )
    data_concessao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Desconto na Anuidade"
        verbose_name_plural = "Descontos nas Anuidades"

    def __str__(self):
        return f"Desconto de R$ {self.valor_desconto} para {self.anuidade_associado}"


# Tipo de Despesa
class TipoDespesaModel(models.Model):
    nome = models.CharField(max_length=255, unique=True, verbose_name="Nome do Tipo de Despesa")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    class Meta:
        ordering = ['nome']
        verbose_name = "Tipo de Despesa"
        verbose_name_plural = "Tipos de Despesas"

    def __str__(self):
        return self.nome

# Despesa de uma Associação
class DespesaAssociacaoModel(models.Model):
    associacao = models.ForeignKey(
        'app_associacao.AssociacaoModel',
        on_delete=models.CASCADE,
        related_name='despesas',
        verbose_name="Associação"
    )
    reparticao = models.ForeignKey(
        'app_associacao.ReparticoesModel',
        on_delete=models.SET_NULL,
        related_name='despesas',
        verbose_name="Repartição",
        blank=True,
        null=True
    )
    tipo_despesa = models.ForeignKey(
        TipoDespesaModel,
        on_delete=models.PROTECT,
        related_name='despesas',
        verbose_name="Tipo de Despesa"
    )
    valor = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor da Despesa")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    numero_nota_fiscal = models.CharField(max_length=150, blank=True, null=True, verbose_name="Número da Nota Fiscal")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_lancamento = models.DateTimeField(default=now, verbose_name="Data de Lançamento")  # ✅ Agora pode ser editado!
    registrado_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='Registros',
        verbose_name="Registrado por"
    )
    pago = models.BooleanField(default=False, verbose_name="Despesa Paga")  # ✅ Adicionado!

    class Meta:
        ordering = ['-data_vencimento']
        verbose_name = "Despesa da Associação"
        verbose_name_plural = "Despesas das Associações"

    def __str__(self):
        return f"{self.tipo_despesa.nome} - {self.associacao.nome_fantasia} - R$ {self.valor} - Vencimento: {self.data_vencimento} - Reparticão: {self.reparticao}  - Pago: {'Sim' if self.pago else 'Não'}"

    def save(self, *args, **kwargs):
        """ 
        Compara os valores antigos antes de salvar e registra as alterações corretamente.
        """
        from .models import DespesaAlteracaoModel  # Importa o modelo de histórico
        
        usuario_atualizacao = kwargs.pop('usuario_atualizacao', None)  # Obtém o usuário logado
        if not usuario_atualizacao:
            usuario_atualizacao = getattr(self, 'usuario_atualizacao', None)  # Fallback

        if self.pk:
            despesa_antiga = DespesaAssociacaoModel.objects.get(pk=self.pk)  # Obtém os dados antigos
            
            campos_monitorados = ['associacao', 'reparticao', 'tipo_despesa', 'valor', 'descricao', 'numero_nota_fiscal', 'data_vencimento', 'pago']
            
            for campo in campos_monitorados:
                valor_anterior = getattr(despesa_antiga, campo)
                valor_novo = getattr(self, campo)

                # Apenas registra se houve alteração
                if valor_anterior != valor_novo and usuario_atualizacao:
                    DespesaAlteracaoModel.objects.create(
                        despesa=self,
                        campo_alterado=campo,
                        valor_anterior=str(valor_anterior),
                        valor_novo=str(valor_novo),
                        alterado_por=usuario_atualizacao  # ✅ Agora pega corretamente o usuário logado!
                    )

        super().save(*args, **kwargs) # Continua o processo normal de salvar
            
    def esta_vencida(self):
        """Verifica se a despesa está vencida."""
        return now().date() > self.data_vencimento


class DespesaAlteracaoModel(models.Model):
    despesa = models.ForeignKey(
        'DespesaAssociacaoModel', 
        on_delete=models.CASCADE, 
        related_name='alteracoes', 
        verbose_name="Despesa"
    )
    campo_alterado = models.CharField(max_length=100, verbose_name="Campo Alterado")
    valor_anterior = models.TextField(blank=True, null=True, verbose_name="Valor Anterior")
    valor_novo = models.TextField(blank=True, null=True, verbose_name="Valor Novo")
    alterado_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Alterado por"
    )
    data_alteracao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Alteração")

    class Meta:
        ordering = ['-data_alteracao']
        verbose_name = "Alteração de Despesa"
        verbose_name_plural = "Alterações de Despesas"

    def __str__(self):
        return f"{self.campo_alterado} alterado por {self.alterado_por} em {self.data_alteracao.strftime('%d/%m/%Y %H:%M')}"


# ENTRADAS
# Tipo de Serviço
class TipoServicoModel(models.Model):
    nome = models.CharField(max_length=255, unique=True, verbose_name="Nome do Tipo de Serviço")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    class Meta:
        ordering = ['nome']
        verbose_name = "Tipo de Serviço"
        verbose_name_plural = "Tipos de Serviços"

    def __str__(self):
        return self.nome

# Entradas Financeiras de uma Associação
class EntradaFinanceira(models.Model):
    FORMA_PAGAMENTO_CHOICES = [
        ('pix', 'PIX'),
        ('credito', 'Cartão de Crédito'),
        ('debito', 'Cartão de Débito'),
        ('deposito', 'Depósito'),
        ('dinheiro', 'Dinheiro'),
    ]

    PARCELAMENTO_CHOICES = [
        ('avista', 'Pagamento à Vista'),
        ('duas_parcelas', 'Duas Parcelas'),
        ('tres_parcelas', 'Três Parcelas'),
    ]

    STATUS_PAGAMENTO_CHOICES = [
        ('pendente', 'Pendente'),
        ('parcial', 'Parcial'),
        ('pago', 'Pago'),
    ]

    associacao = models.ForeignKey(
        'app_associacao.AssociacaoModel',
        on_delete=models.CASCADE,
        related_name='entradas',
        verbose_name="Associação"
    )
    reparticao = models.ForeignKey(
        'app_associacao.ReparticoesModel',
        on_delete=models.SET_NULL,
        related_name='entradas',
        verbose_name="Repartição",
        blank=True,
        null=True
    )
    tipo_servico = models.ForeignKey(
        'app_finances.TipoServicoModel',
        on_delete=models.PROTECT,
        related_name='entradas',
        verbose_name="Tipo de Serviço"
    )
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total")
    forma_pagamento = models.CharField(max_length=10, choices=FORMA_PAGAMENTO_CHOICES, verbose_name="Forma de Pagamento")
    parcelamento = models.CharField(max_length=15, choices=PARCELAMENTO_CHOICES, verbose_name="Parcelamento")
    status_pagamento = models.CharField(max_length=10, choices=STATUS_PAGAMENTO_CHOICES, default="pendente", verbose_name="Status do Pagamento", editable=False)
    
    data_criacao = models.DateTimeField(default=now, verbose_name="Data de Criação")
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Criado por")
    valor_pagamento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),  # 🔥 Usa Decimal para evitar erros
        blank=True,
        null=True,
        verbose_name="Valor Pago"
    )
    # Em app_finances.models.py
    servico_extra = models.OneToOneField(
        'app_servicos.ServicoExtraAssociadoModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entrada_servico_extra',  # 💡 ALTERADO AQUI!
        verbose_name="Serviço Extra Vinculado"
    )
    

    def save(self, *args, **kwargs):
        """
        Antes de salvar, verifica se houve alterações e registra no histórico.
        """
        if not self.criado_por_id:  # 🔍 Se ainda não tem um usuário associado
            raise ValueError("O campo 'criado_por' é obrigatório antes de salvar.")  # 🚨 Evita erro de integridade

        if self.pk:  # ✅ Só registra alterações se a entrada já existir
            entrada_antiga = EntradaFinanceira.objects.get(pk=self.pk)
            dados_anteriores = model_to_dict(entrada_antiga)  # Valores antes da alteração
            dados_novos = model_to_dict(self)  # Novos valores
            
            campos_a_monitorar = [
            'associacao', 'reparticao','tipo_servico',
                'descricao', 'valor_total', 'forma_pagamento', 'parcelamento', 'status_pagamento'
            ]

            alteracoes = []
            for campo in campos_a_monitorar:
                valor_antigo = str(dados_anteriores.get(campo, ""))
                valor_novo = str(dados_novos.get(campo, ""))
                
                if valor_antigo != valor_novo:  # Só registra mudanças reais
                    alteracoes.append(EntradaAlteracaoModel(
                        entrada=self,
                        campo_alterado=campo.replace("_", " ").capitalize(),
                        valor_anterior=valor_antigo,
                        valor_novo=valor_novo,
                        alterado_por=self.criado_por
                    ))

            # 🔥 Salva todas as alterações de uma vez (melhor desempenho)
            if alteracoes:
                EntradaAlteracaoModel.objects.bulk_create(alteracoes)

        # 🔹 Garante que `valor_pagamento` nunca seja None
        if self.valor_pagamento is None:
            self.valor_pagamento = Decimal("0.00")

        super().save(*args, **kwargs)  # 🔥 Agora salva no banco normalmente

        

    def calcular_pagamento(self):
        """ Atualiza o valor restante e o status do pagamento. """
        total_pago = self.pagamentos.aggregate(total=Sum("valor_pago"))["total"] or Decimal('0.00')
        
        # 🔹 Atualiza o valor do campo "valor_pagamento"
        self.valor_pagamento = total_pago

        # 🔹 Atualiza status com base no saldo restante
        saldo_restante = self.valor_total - total_pago
        if saldo_restante <= Decimal('0.00'):
            self.status_pagamento = "pago"
        elif total_pago > Decimal('0.00'):
            self.status_pagamento = "parcial"
        else:
            self.status_pagamento = "pendente"

        self.save(update_fields=["valor_pagamento", "status_pagamento"])



class PagamentoEntrada(models.Model):
    entrada = models.ForeignKey(EntradaFinanceira, on_delete=models.CASCADE, related_name="pagamentos")
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    data_pagamento = models.DateTimeField(default=now)
    registrado_por = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # 🔥 Após registrar o pagamento, recalcula o status da entrada
        self.entrada.calcular_pagamento()

    def __str__(self):
        return f"Pagamento de R$ {self.valor_pago} em {self.data_pagamento.strftime('%d/%m/%Y')} - Entrada {self.entrada.id}"


# Alterações de Entradas
class EntradaAlteracaoModel(models.Model):
    entrada = models.ForeignKey(
        'EntradaFinanceira', 
        on_delete=models.CASCADE, 
        related_name='alteracoes', 
        verbose_name="Entrada",
        default=None,
        null=True, blank=True, 
    )
    campo_alterado = models.CharField(max_length=100, verbose_name="Campo Alterado")
    valor_anterior = models.TextField(blank=True, null=True, verbose_name="Valor Anterior")
    valor_novo = models.TextField(blank=True, null=True, verbose_name="Valor Novo")
    alterado_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Alterado por"
    )
    data_alteracao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Alteração")

    class Meta:
        ordering = ['-data_alteracao']
        verbose_name = "Alteração de Entrada"
        verbose_name_plural = "Alterações de Entradas"

    def __str__(self):
        return f"{self.campo_alterado} alterado por {self.alterado_por} em {self.data_alteracao.strftime('%d/%m/%Y %H:%M')}"

