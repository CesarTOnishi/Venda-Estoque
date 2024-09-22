from django.db import models
from cliente.models import Cliente
from django.utils import timezone


class Carrinho(models.Model):
    user_id = models.IntegerField(null=True, blank=True)
    produto_id = models.IntegerField(null=True, blank=True)
    quantidade = models.IntegerField(null=True, blank=True)
    valor_unitario = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

class View_Carrinho(models.Model):
    produto_id = models.IntegerField(null=True, blank=True)
    id = models.IntegerField(default=1, primary_key=True)
    user_id = models.IntegerField(null=True, blank=True)
    nome = models.CharField(max_length=50)
    quantidade = models.IntegerField(null=True, blank=True)
    valor_unitario = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    qt_itens = models.IntegerField(null=True, blank=True)
    class Meta:
        managed = False
        db_table = 'View_Carrinho'

class Pedido(models.Model):
    nr_pedido = models.IntegerField(null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)  # Use ForeignKey para relacionar com Cliente
    produto_id = models.IntegerField(null=True, blank=True)
    quantidade = models.IntegerField(null=True, blank=True)
    valor_unitario = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    data_pedido = models.DateField(blank=True, null=True)
    
    class Meta:
        db_table = 'venda_pedido'

class View_Pedido(models.Model):
    produto_id = models.IntegerField(null=True, blank=True)
    id = models.IntegerField(default=1, primary_key=True)
    user_id = models.IntegerField(null=True, blank=True)
    nr_pedido = models.IntegerField(default=1, null=True, blank=True)
    nome = models.CharField(max_length=50)
    quantidade = models.IntegerField(null=True, blank=True)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cliente_nome = models.CharField(max_length=100, null=True, blank=True)
    data_pedido = models.DateField(blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'View_Pedido'