# Generated by Django 5.1.3 on 2024-12-24 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_associacao', '0003_integrantesmodel_estado_civil_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='integrantesmodel',
            name='nacionalidade',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Nacionalidade'),
        ),
    ]
