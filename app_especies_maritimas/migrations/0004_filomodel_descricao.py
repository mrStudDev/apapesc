# Generated by Django 5.1.7 on 2025-04-04 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_especies_maritimas', '0003_alter_ameacamodel_especie_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='filomodel',
            name='descricao',
            field=models.TextField(blank=True),
        ),
    ]
