from django.db import models

class Fornecedor(models.Model):
    tipo_pessoa = models.CharField(max_length=15, null=True) 
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, blank=True, null=True, unique=True)
    cnpj = models.CharField(max_length=18, blank=True, null=True, unique=True)
    endereco = models.CharField(max_length=255)
    numero = models.CharField(max_length=10) 
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=15)

    class Meta:
        ordering = ['nome']
        verbose_name = 'fornecedor'
        verbose_name_plural = 'fornecedores'

    def __str__(self):
        return self.nome
