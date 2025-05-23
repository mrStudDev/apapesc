# Generated by Django 5.1.7 on 2025-03-20 01:51

import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_finances', '0009_alter_entradaalteracaomodel_entrada_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entradaalteracaomodel',
            name='entrada',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='alteracoes', to='app_finances.entradafinanceira', verbose_name='Entrada'),
        ),
        migrations.AlterField(
            model_name='entradafinanceira',
            name='valor_pagamento',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=10, null=True, verbose_name='Valor Pago'),
        ),
        migrations.AlterField(
            model_name='pagamentoentrada',
            name='entrada',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagamentos', to='app_finances.entradafinanceira'),
        ),
    ]
