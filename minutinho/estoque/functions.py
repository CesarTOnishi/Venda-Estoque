from django.db import models, connection

def deletarProduto(prod_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM estoque_produto where id = %s", [prod_id])

def removerCategoria(cat_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM estoque_categoria where id = %s", [cat_id])