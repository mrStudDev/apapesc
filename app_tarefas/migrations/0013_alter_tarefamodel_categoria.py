# Generated by Django 5.1.3 on 2025-02-24 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_tarefas', '0012_delete_notificacaomodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarefamodel',
            name='categoria',
            field=models.CharField(choices=[('administrativa', 'Administrativa'), ('associado', 'Associado'), ('integrante', 'Integrante'), ('sistema', 'Sistema'), ('outro', 'Outro')], default='outro', max_length=20, verbose_name='Categoria'),
        ),
    ]
