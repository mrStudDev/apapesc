# Generated by Django 5.1.7 on 2025-04-18 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_especies_maritimas', '0005_alter_ameacamodel_especie_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='especiemarinhamodel',
            name='code',
            field=models.PositiveIntegerField(blank=True, null=True, unique=True),
        ),
    ]
