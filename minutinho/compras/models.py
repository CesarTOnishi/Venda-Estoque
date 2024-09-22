from django.db import models
from django.utils import timezone

from estoque.models import Produto
from fornecedor.models import Fornecedor

class PedidoCompra(models.Model):
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE)
    data_pedido = models.DateField(default=timezone.now)  # Data do pedido
    produtos = models.ManyToManyField(Produto, through='PedidoProduto')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def calcular_total(self):
        total = sum([item.quantidade * item.preco_unitario for item in self.pedidoproduto_set.all()])
        self.total = total
        self.save()

    def __str__(self):
        return f"Pedido {self.id} - {self.fornecedor.nome}"


class PedidoProduto(models.Model):
    pedido = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.produto.nome} - {self.quantidade} x {self.preco_unitario}"
    