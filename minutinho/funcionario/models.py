from django.db import models

class Funcionarios(models.Model):
    nome = models.CharField(max_length=40)
    cpf = models.CharField(max_length=14, blank=True, unique=True)
    email = models.CharField(max_length=100, blank=True)
    cargo = models.CharField(max_length=100, blank=True)
    salario = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    data_admissao = models.DateTimeField(auto_now_add=True)
    telefone = models.CharField(max_length=20, blank=True)
    endereco = models.CharField(max_length=200, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome']
        verbose_name = 'funcionário'
        verbose_name_plural = 'funcionários'
