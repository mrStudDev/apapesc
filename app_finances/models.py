from django.shortcuts import render
from django.contrib.auth.models import User 
from django.db import models, transaction
from django.utils import timezone
from decimal import Decimal
from app_associados.models import AssociadoModel, AssociacaoModel
from django.utils.timezone import now
from django.db.models import Sum, Q
from django.apps import apps 
from django.conf import settings


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
        Atribui esta anuidade a todos os associados, calculando pro-rata.
        """
        # Evita import circular com app_associados
        AssociadoModel = apps.get_model('app_associados', 'AssociadoModel')
        AnuidadeAssociado = apps.get_model('app_finances', 'AnuidadeAssociado')

        associados = AssociadoModel.objects.all()

        with transaction.atomic():
            for associado in associados:
                # Se já existir AnuidadeAssociado para este anuidade + associado, pula
                if not AnuidadeAssociado.objects.filter(anuidade=self, associado=associado).exists():
                    meses_restantes = self.calcular_meses_validos(associado)
                    if meses_restantes > 0:
                        valor_pro_rata = round(
                            (self.valor_anuidade / Decimal(12)) * Decimal(meses_restantes), 2
                        )
                        AnuidadeAssociado.objects.create(
                            anuidade=self,
                            associado=associado,
                            valor_pro_rata=valor_pro_rata
                        )

    def calcular_meses_validos(self, associado):
        """
        Calcula o número de meses para o cálculo pro-rata
        com base em associado.data_filiacao e self.ano.
        """
        if not associado.data_filiacao or associado.data_filiacao.year > self.ano:
            return 0
        if associado.data_filiacao.year == self.ano:
            return 12 - associado.data_filiacao.month + 1
        return 12


class AnuidadeAssociado(models.Model):
    anuidade = models.ForeignKey(AnuidadeModel, on_delete=models.CASCADE, related_name='anuidades_associados')
    associado = models.ForeignKey(
        'app_associados.AssociadoModel',
        on_delete=models.CASCADE,
        related_name='anuidades_associados'
    )
    valor_pro_rata = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Pro-Rata")
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
        return max(self.valor_pro_rata - self.valor_pago, Decimal('0.00'))

    def dar_baixa(self, valor_baixa):
        """Dá baixa parcial ou total no valor da anuidade, sem criar automaticamente o pagamento."""
        self.valor_pago += valor_baixa
        if self.valor_pago >= self.valor_pro_rata:
            self.pago = True
        self.save()


class Pagamento(models.Model):
    anuidade_associado = models.ForeignKey(AnuidadeAssociado, on_delete=models.CASCADE, related_name='pagamentos')
    data_pagamento = models.DateField(auto_now_add=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Pago")
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Registrado por")

    def __str__(self):
        return f"Pagamento de R$ {self.valor} em {self.data_pagamento}"
    
    



# Tipo de Despesa
class TipoDespesaModel(models.Model):
    nome = models.CharField(max_length=255, unique=True, verbose_name="Tipo de Despesa")

    class Meta:
        verbose_name = "Tipo de Despesa"
        verbose_name_plural = "Tipos de Despesa"

    def __str__(self):
        return self.nome


# Despesa de uma Associação
class DespesaAssociacaoModel(models.Model):
    associacao = models.ForeignKey(AssociadoModel, on_delete=models.CASCADE, related_name='despesas')
    tipo_despesa = models.ForeignKey(TipoDespesaModel, on_delete=models.PROTECT, related_name='despesas')
    valor = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor da Despesa")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    numero_nota_fiscal = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número da Nota Fiscal")
    data_despesa = models.DateField(verbose_name="Data da Despesa")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_lancamento = models.DateTimeField(auto_now_add=True, verbose_name="Data de Lançamento")
    registrado_por = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Registrado por")

    class Meta:
        ordering = ['-data_despesa']
        verbose_name = "Despesa da Associação"
        verbose_name_plural = "Despesas das Associações"

    def __str__(self):
        return f"{self.tipo_despesa.nome} - {self.associacao.nome_fantasia} - R$ {self.valor}"

    def esta_vencida(self):
        """Verifica se a despesa está vencida."""
        return now().date() > self.data_vencimento

