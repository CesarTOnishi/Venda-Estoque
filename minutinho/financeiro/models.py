from django.db import models
from django.utils import timezone
from compras.models import PedidoCompra
from venda.models import Pedido

class ContaPagar(models.Model):
    pedido = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE, null=True, blank=True)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pagamento = models.CharField(max_length=50, null=True)
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    pago = models.BooleanField(default=False)
    criacao = models.DateTimeField(auto_now_add=True)
    numero_parcela = models.PositiveIntegerField(null=True)

    def __str__(self):
        return f"Pagar: {self.descricao} - R$ {self.valor}"

    def pagar(self):
        if not self.pago:
            self.pago = True
            self.data_pagamento = timezone.now().date()
            self.save()

            if not Extrato.objects.filter(descricao=f"Pagamento: {self.descricao}", valor=self.valor, tipo="saida").exists():
                Extrato.objects.create(
                    descricao=f"Pagamento: {self.descricao}",
                    valor=self.valor,
                    tipo='saida',
                    status='pago'
                )


class ContaReceber(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, null=True, blank=True)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    data_recebimento = models.DateField(null=True, blank=True)
    metodo_pagamento = models.CharField(max_length=50, blank=True, null=True)
    recebido = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    numero_parcela = models.IntegerField(default=1)
    editavel = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Receber: {self.descricao} - R$ {self.valor}"

    def receber(self):
        if not self.recebido:
            self.recebido = True
            self.data_recebimento = timezone.now().date()
            self.save()

            if not Extrato.objects.filter(descricao=f"Recebimento: {self.descricao} (Parcela {self.numero_parcela})", valor=self.valor, tipo="entrada").exists():
                Extrato.objects.create(
                    descricao=f"Recebimento: {self.descricao} (Parcela {self.numero_parcela})",
                    valor=self.valor,
                    tipo='entrada',
                    status='pago'
                )

class Extrato(models.Model):
    TIPO_CHOICES = (
        ('entrada', 'Entrada'), 
        ('saida', 'Saída'), 
    )

    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('nao_pago', 'Não Pago'),
    )

    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_transacao = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES) 
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    metodo_pagamento = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    conta_pagar = models.ForeignKey(ContaPagar, on_delete=models.SET_NULL, null=True, blank=True)
    conta_receber = models.ForeignKey(ContaReceber, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        ultimo_saldo = Extrato.objects.filter(data_transacao__lt=self.data_transacao).order_by('-data_transacao').first()
        saldo_anterior = ultimo_saldo.saldo if ultimo_saldo else 0

        if self.status == 'pago':
            if self.tipo == 'entrada':
                self.saldo = saldo_anterior + self.valor 
            elif self.tipo == 'saida':
                self.saldo = saldo_anterior - self.valor 
        else:
            self.saldo = saldo_anterior

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.descricao} - {self.tipo} - R$ {self.valor}"
