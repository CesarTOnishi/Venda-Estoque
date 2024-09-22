from django.db import models
from django.core.exceptions import ValidationError
from datetime import date


class Cliente(models.Model):
    nome = models.CharField(max_length=40)
    cidade = models.CharField(max_length=40)
    estado = models.CharField(max_length=40, null=True, blank=True)
    cpf = models.CharField(max_length=11, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.nome

    def clean(self):
        if not self.cpf.isdigit() or len(self.cpf) != 11:
            raise ValidationError('O CPF deve ter 11 dígitos numéricos.')
        
        if self.data_nascimento:
            hoje = date.today()
            if self.data_nascimento > hoje:
                raise ValidationError('A data de nascimento não pode ser no futuro.')

    def idade(self):
        if self.data_nascimento:
            hoje = date.today()
            return hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return None
    
    class Meta:
        db_table = 'cliente_cliente'
        ordering = ['nome']
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

