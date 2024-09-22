from django.db import connection

def deletarCompra(item_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM compras_pedidoproduto WHERE pedido_id = %s", [item_id])
        cursor.execute("DELETE FROM compras_pedidocompra WHERE id = %s", [item_id])
