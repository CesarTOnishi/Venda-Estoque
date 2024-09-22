from django.db import models, connection
from cliente.models import Cliente

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def removerCliente(cli_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM venda_pedido WHERE cliente_id = %s", [cli_id])
            
            cursor.execute("DELETE FROM cliente_cliente WHERE id = %s", [cli_id])
    except Exception as e:
        print(f"Erro ao remover cliente: {e}")