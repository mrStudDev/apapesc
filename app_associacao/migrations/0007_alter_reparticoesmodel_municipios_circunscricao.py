# Generated by Django 5.1.3 on 2024-12-26 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_associacao', '0006_integrantesmodel_oab'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reparticoesmodel',
            name='municipios_circunscricao',
            field=models.ManyToManyField(blank=True, default='', max_length=100, related_name='municipios_circunscricao', to='app_associacao.municipiosmodel', verbose_name='Municipios Circinscrição'),
        ),
    ]