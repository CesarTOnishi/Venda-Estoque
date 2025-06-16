from decimal import Decimal
from django.db import models, transaction
from django.utils import timezone
from datetime import timedelta
from estoque.models import Produto
from fornecedor.models import Fornecedor

class PedidoCompra(models.Model):
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE)
    data_pedido = models.DateField(default=timezone.now) 
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    numero_parcela = models.IntegerField(default=1)
    parcelas = models.PositiveIntegerField(default=1)

    def calcular_total(self):
        if self.pk:  # esse comando verifica se ja foi salvo
            total = sum(
                item.quantidade * item.preco_unitario
                for item in self.pedidoproduto_set.all()
            )
            self.total = total
            return total 
        else:
            self.total = Decimal('0.00')
            return Decimal('0.00')

    def salvar_parcelas(self):
        if self.parcelas > 1:
            valor_parcela = self.total / self.parcelas
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
        if not self.pk:
            super().save(*args, **kwargs)
        
        self.total = self.calcular_total()  
        
        super().save(*args, **kwargs)


class PedidoProduto(models.Model):
    pedido = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs) 
        self.pedido.calcular_total() 
        self.pedido.save()  

        def __str__(self):
            return f"{self.produto.nome} - {self.quantidade} x {self.preco_unitario}"
    
class ParcelaPedido(models.Model):
    pedido = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE, related_name="parcelas_pedido")
    numero_parcela = models.PositiveIntegerField() 
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    pago = models.BooleanField(default=False)


    def __str__(self):
        return f"Pedido {self.pedido.id} - Parcela {self.numero_parcela}/{self.pedido.parcelas} - R$ {self.valor_parcela}"
