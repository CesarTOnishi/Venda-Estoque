from django.db import models
from cliente.models import Cliente
from estoque.models import Produto
from condicaoPagamento.models import CondicaoPagamento
from django.utils import timezone
from datetime import timedelta
from django.db import connection,  transaction


class Carrinho(models.Model):
    user_id = models.IntegerField(null=True, blank=True)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, null=True, blank=True, db_column='produto_id')
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
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)  
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, null=True, blank=True, db_column='produto_id')
    quantidade = models.IntegerField(null=True, blank=True)
    valor_unitario = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    data_pedido = models.DateField(blank=True, null=True)
    metodo_pagamento = models.CharField(max_length=50, blank=True, null=True)
    parcelas = models.IntegerField(null=True, blank=True, default=1)
    condicao_pagamento = models.ForeignKey(CondicaoPagamento, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'venda_pedido'

    def salvar_parcelas(self):
        """Cria parcelas automaticamente ao salvar um pedido parcelado."""
        if self.parcelas > 1:
            valor_parcela = self.valor_total / self.parcelas
            data_base = self.data_pedido or timezone.now().date()

            with transaction.atomic():
                for i in range(self.parcelas):
                    data_vencimento = data_base + timedelta(days=(i + 1) * 30)
                    ParcelaPedido.objects.create(
                        pedido=self,
                        numero_parcela=i + 1,
                        valor_parcela=valor_parcela,
                        data_vencimento=data_vencimento
                    )

    def save(self, *args, **kwargs):
        novo_pedido = self.pk is None 
        super().save(*args, **kwargs)

        if novo_pedido:
            self.salvar_parcelas()  

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
    metodo_pagamento = models.CharField(max_length=50, blank=True, null=True)
    parcelas = models.IntegerField(null=True, blank=True, default=1)
    condicao_pagamento_nome = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'View_Pedido'

from django.db import models

class ParcelaPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='parcelas_pedido')
    numero_parcela = models.IntegerField()
    valor_parcela = models.DecimalField(max_digits=15, decimal_places=2)
    data_vencimento = models.DateField()
    pago = models.BooleanField(default=False)

    def __str__(self):
        return f"Parcela {self.numero_parcela} - Pedido #{self.pedido.id}"

