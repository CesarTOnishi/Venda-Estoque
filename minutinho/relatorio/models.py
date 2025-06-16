from django.db import models
from estoque.models import Produto 

class RelatorioVenda(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE) 
    quantidade_vendida = models.IntegerField() 
    data_relatorio = models.DateField(auto_now_add=True) 

    class Meta:
        verbose_name = "Relatório Venda"
        verbose_name_plural = "Relatório Venda"
        ordering = ['-quantidade_vendida']  

    def __str__(self):
        return f"{self.produto.nome} - {self.quantidade_vendida} unidades vendidas"