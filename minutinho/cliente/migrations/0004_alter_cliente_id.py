# Generated by Django 4.2.5 on 2024-09-01 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0003_cliente_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='id',
            field=models.IntegerField(default=1, primary_key=True, serialize=False),
        ),
    ]