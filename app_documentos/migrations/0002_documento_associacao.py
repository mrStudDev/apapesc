# Generated by Django 5.1.3 on 2024-12-22 21:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_associacao', '0002_alter_integrantesmodel_user'),
        ('app_documentos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='associacao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='associacao_documentos', to='app_associacao.associacaomodel'),
        ),
    ]