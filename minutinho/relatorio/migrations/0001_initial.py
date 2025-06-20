# Generated by Django 4.2.5 on 2024-09-25 15:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('estoque', '0003_alter_produto_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelatorioVenda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade_vendida', models.IntegerField()),
                ('data_relatorio', models.DateField(auto_now_add=True)),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estoque.produto')),
            ],
            options={
                'verbose_name': 'Relatório Venda',
                'verbose_name_plural': 'Relatório Venda',
                'ordering': ['-quantidade_vendida'],
            },
        ),
    ]
