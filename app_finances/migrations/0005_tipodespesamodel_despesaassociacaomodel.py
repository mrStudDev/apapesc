# Generated by Django 5.1.3 on 2025-02-02 23:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_associacao', '0010_alter_associacaomodel_diretores'),
        ('app_finances', '0004_pagamento_registrado_por'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoDespesaModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255, unique=True, verbose_name='Tipo de Despesa')),
            ],
            options={
                'verbose_name': 'Tipo de Despesa',
                'verbose_name_plural': 'Tipos de Despesa',
            },
        ),
        migrations.CreateModel(
            name='DespesaAssociacaoModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Valor da Despesa')),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descrição')),
                ('numero_nota_fiscal', models.CharField(blank=True, max_length=50, null=True, verbose_name='Número da Nota Fiscal')),
                ('data_despesa', models.DateField(verbose_name='Data da Despesa')),
                ('data_vencimento', models.DateField(verbose_name='Data de Vencimento')),
                ('data_lancamento', models.DateTimeField(auto_now_add=True, verbose_name='Data de Lançamento')),
                ('associacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='despesas', to='app_associacao.associacaomodel')),
                ('registrado_por', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Registrado por')),
                ('tipo_despesa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='despesas', to='app_finances.tipodespesamodel')),
            ],
            options={
                'verbose_name': 'Despesa da Associação',
                'verbose_name_plural': 'Despesas das Associações',
                'ordering': ['-data_despesa'],
            },
        ),
    ]
