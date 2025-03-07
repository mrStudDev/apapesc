# Generated by Django 5.1.3 on 2024-12-25 18:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_associacao', '0006_integrantesmodel_oab'),
        ('app_associados', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tarefa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255)),
                ('descricao', models.CharField(blank=True, max_length=255, null=True, verbose_name='Breve Descrição')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('data_conclusao', models.DateTimeField(blank=True, null=True, verbose_name='Data Conlusão')),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('em_andamento', 'Em Andamento'), ('concluida', 'Concluída'), ('devolvida', 'Devolvida'), ('arquivada', 'Arquivada'), ('desarquivada', 'Desarquivada')], default='aberta', max_length=20, verbose_name='status da Tarefa')),
                ('categoria', models.CharField(choices=[('administrativa', 'Administrativa'), ('associado', 'Associado'), ('integrante', 'Integrante'), ('outro', 'Outro')], default='outro', max_length=20, verbose_name='Categoria')),
                ('prioridade', models.CharField(choices=[('alta', 'Alta'), ('media', 'Média'), ('baixa', 'Baixa')], default='media', max_length=20, verbose_name='Prioridade')),
                ('content', models.TextField(blank=True, null=True, verbose_name='Anotações')),
                ('associado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_associados.associadomodel', verbose_name='Associado')),
                ('criado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tarefas_criadas', to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
                ('responsaveis', models.ManyToManyField(related_name='tarefas_atribuidas', to='app_associacao.integrantesmodel', verbose_name='Responsáveis')),
            ],
        ),
    ]
