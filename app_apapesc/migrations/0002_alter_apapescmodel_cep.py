# Generated by Django 5.1.3 on 2024-12-08 17:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_apapesc', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apapescmodel',
            name='cep',
            field=models.CharField(blank=True, default='', max_length=9, null=True, validators=[django.core.validators.RegexValidator('^\\d{5}-\\d{3}$', 'CEP deve estar no formato 00000-000.')], verbose_name='CEP'),
        ),
    ]