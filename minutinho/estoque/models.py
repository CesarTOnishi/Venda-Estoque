from django.db import models
 
class Produto(models.Model):
    nome = models.CharField(max_length=40)
    estoque = models.IntegerField(default=0)
    descricao = models.CharField(max_length=255, null=True, blank=True)
    preco = models.DecimalField(max_digits=20, decimal_places=2)

class Meta:
    ordering=['nome']
    verbose_name= 'produto'
    verbose_name_plural= 'produto'
