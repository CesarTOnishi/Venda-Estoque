# Generated by Django 4.2.5 on 2025-02-25 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compras', '0002_remove_pedidocompra_produtos'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedidocompra',
            name='numero_parcela',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='pedidocompra',
            name='parcelas',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
