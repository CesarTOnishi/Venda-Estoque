# Generated by Django 4.2.5 on 2025-02-25 22:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('compras', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedidocompra',
            name='produtos',
        ),
    ]
