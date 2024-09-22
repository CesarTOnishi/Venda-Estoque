from django import forms
from .models import PedidoCompra, PedidoProduto
from fornecedor.models import Fornecedor
from estoque.models import Produto

class PedidoCompraForm(forms.ModelForm):
    fornecedor = forms.ModelChoiceField(
        queryset=Fornecedor.objects.all(),
        widget=forms.Select(attrs={'class': 'select2', 'id': 'fornecedor-select'}),
        label="Fornecedor"
    )
    data_pedido = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2100)), label="Data do Pedido")

    class Meta:
        model = PedidoCompra
        fields = ['fornecedor', 'data_pedido']

class PedidoProdutoForm(forms.ModelForm):
    produto = forms.ModelChoiceField(queryset=Produto.objects.all(), label="Produto", widget=forms.Select)
    quantidade = forms.IntegerField(min_value=1, label="Quantidade")
    preco_unitario = forms.DecimalField(max_digits=10, decimal_places=2, label="Preço Unitário")

    class Meta:
        model = PedidoProduto
        fields = ['produto', 'quantidade', 'preco_unitario']
