# Generated by Django 5.1.3 on 2024-12-23 22:42

import app_automacoes.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeclaracaoFiliacaoModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdf_base', models.FileField(help_text='Substituirá o arquivo base atual para a declaração de filiação.', upload_to=app_automacoes.models.upload_to_declaracao_filiacao, verbose_name='PDF Base para Declaração de Filiação')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Última Atualização')),
            ],
        ),
        migrations.CreateModel(
            name='DeclaracaoResidenciaModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdf_base', models.FileField(help_text='Substituirá o arquivo base atual para a declaração de residência.', upload_to=app_automacoes.models.upload_to_declaracao_residencia, verbose_name='PDF Base para Declaração de Residência')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Última Atualização')),
            ],
        ),
    ]