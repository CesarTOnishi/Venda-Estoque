# Generated by Django 4.2.5 on 2025-02-22 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0004_contareceber_numero_parcela'),
    ]

    operations = [
        migrations.AddField(
            model_name='extrato',
            name='metodo_pagamento',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
