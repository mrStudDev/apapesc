# Generated by Django 5.1.3 on 2024-12-22 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_documentos', '0002_documento_associacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='nome',
            field=models.CharField(blank=True, max_length=1500, verbose_name='Nome do Documento'),
        ),
        migrations.AlterField(
            model_name='tipodocumentomodel',
            name='tipo',
            field=models.CharField(max_length=1500, verbose_name='Nome do Tipo de Documento'),
        ),
    ]
