# Generated by Django 5.1.7 on 2025-05-28 23:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_tarefas', '0013_rodadaprocessamentoinss_guiarodadaprocessada'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rodadaprocessamentoinss',
            name='lancamento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_tarefas.lancamentoinssmodel'),
        ),
    ]
