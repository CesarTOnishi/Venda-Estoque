from django.db import models, connection

def deletarProduto(prod_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM estoque_produto where id = %s", [prod_id])