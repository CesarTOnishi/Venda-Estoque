# Generated by Django 4.2.5 on 2023-10-19 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Carrinho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('produto_id', models.IntegerField(blank=True, null=True)),
                ('valor_unitario', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('valor_total', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
            ],
        ),
    ]