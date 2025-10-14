from django.db import models
from cliente.models import Cliente
from estoque.models import Produto
from funcionario.models import Funcionarios
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
    funcionario = models.ForeignKey(Funcionarios, on_delete=models.SET_NULL, null=True, blank=True) 
    quantidade = models.IntegerField(null=True, blank=True)
    valor_unitario = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    data_pedido = models.DateField(blank=True, null=True)

    metodo_pagamento = models.CharField(max_length=50, blank=True, null=True)
    parcelas = models.IntegerField(null=True, blank=True, default=1)

    condicao_pagamento = models.ForeignKey(
        'condicaoPagamento.CondicaoPagamento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    condicao_nome = models.CharField(max_length=100, blank=True, null=True)
    condicao_tipo = models.CharField(max_length=20, blank=True, null=True)
    condicao_parcelas = models.IntegerField(blank=True, null=True)
    condicao_juros = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    condicao_desconto = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'venda_pedido'

    def save(self, *args, **kwargs):
        if self.condicao_pagamento:
            self.condicao_nome = self.condicao_pagamento.nome
            self.condicao_tipo = self.condicao_pagamento.tipo_pagamento
            self.condicao_parcelas = self.condicao_pagamento.parcelas
            self.condicao_juros = self.condicao_pagamento.juros
            self.condicao_desconto = self.condicao_pagamento.desconto

        super().save(*args, **kwargs)


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
    funcionario_nome = models.CharField(max_length=100, null=True, blank=True)
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

