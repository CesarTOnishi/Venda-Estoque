from django.db import connection
from .models import PedidoCompra, PedidoProduto
from financeiro.models import ContaPagar


def deletarCompra(item_id):
    try:
        pedido = PedidoCompra.objects.get(id=item_id)
        itens_pedido = PedidoProduto.objects.filter(pedido=pedido)
        
        for item in itens_pedido:
            produto = item.produto
            produto.estoque -= item.quantidade 
            produto.save()
        
        itens_pedido.delete()
        ContaPagar.objects.filter(pedido=pedido).delete()
        pedido.delete()

    except PedidoCompra.DoesNotExist:
        print(f"Pedido com ID {item_id} não encontrado.")
    except Exception as e:
        print(f"Erro ao deletar o pedido: {e}")
