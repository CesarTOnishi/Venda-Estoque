from django.db import models

class Categoria(models.Model):
    nome = models.CharField(max_length=40)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome']
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

class Produto(models.Model):
    nome = models.CharField(max_length=40)
    estoque = models.IntegerField(default=0)
    descricao = models.CharField(max_length=255, null=True, blank=True)
    preco = models.DecimalField(max_digits=20, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='produtos')


    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome']
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'
