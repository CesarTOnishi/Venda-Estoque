from django.db import models

class CondicaoPagamento(models.Model):
    TIPO_PAGAMENTO_CHOICES = [
        ("credito", "Cartão de Crédito"),
        ("debito", "Cartão de Débito"),
        ("pix", "Pix"),
        ("boleto", "Boleto Bancário"),
        ("transferencia", "Transferência Bancária"),
        ("dinheiro", "Dinheiro"),
    ]

    nome = models.CharField(max_length=100, unique=True) 
    tipo_pagamento = models.CharField(max_length=20, choices=TIPO_PAGAMENTO_CHOICES)
    parcelas = models.IntegerField(default=1)
    juros = models.DecimalField(max_digits=5, decimal_places=2, default=0.0) 
    intervalo_parcelas = models.IntegerField(default=30, help_text="Dias entre parcelas")  
    desconto = models.DecimalField(max_digits=5, decimal_places=2, default=0.0) 
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True) 
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} - {self.parcelas}x ({self.juros}% juros)"

    class Meta:
        verbose_name = "Condição de Pagamento"
        verbose_name_plural = "Condições de Pagamento"
