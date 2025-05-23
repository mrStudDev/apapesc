# Generated by Django 5.1.3 on 2025-03-17 23:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_associacao', '0001_initial'),
        ('app_associados', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='integrantesmodel',
            name='profissao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_associados.profissoesmodel', verbose_name='Profissão'),
        ),
        migrations.AddField(
            model_name='integrantesmodel',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='integrante', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='associacaomodel',
            name='administrador',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='administrador_associacao', to='app_associacao.integrantesmodel', verbose_name='Administrador'),
        ),
        migrations.AddField(
            model_name='associacaomodel',
            name='diretores',
            field=models.ManyToManyField(blank=True, related_name='diretores_associacao', to='app_associacao.integrantesmodel', verbose_name='Diretores'),
        ),
        migrations.AddField(
            model_name='associacaomodel',
            name='presidente',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='presidente_associacao', to='app_associacao.integrantesmodel', verbose_name='Presidente'),
        ),
        migrations.AddField(
            model_name='reparticoesmodel',
            name='associacao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reparticoes', to='app_associacao.associacaomodel', verbose_name='Associação'),
        ),
        migrations.AddField(
            model_name='reparticoesmodel',
            name='delegado',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='delegado_associacao', to='app_associacao.integrantesmodel', verbose_name='Delegado'),
        ),
        migrations.AddField(
            model_name='reparticoesmodel',
            name='municipio_sede',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sedes', to='app_associacao.municipiosmodel'),
        ),
        migrations.AddField(
            model_name='reparticoesmodel',
            name='municipios_circunscricao',
            field=models.ManyToManyField(blank=True, max_length=100, related_name='municipios_circunscricao', to='app_associacao.municipiosmodel', verbose_name='Municipios Circinscrição'),
        ),
        migrations.AddField(
            model_name='integrantesmodel',
            name='reparticao',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='integrantes', to='app_associacao.reparticoesmodel', verbose_name='Repartição'),
        ),
    ]
