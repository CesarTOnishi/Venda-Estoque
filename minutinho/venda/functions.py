from django.db import models, connection
from estoque.models import Produto
from venda.models import Carrinho, View_Carrinho, View_Pedido

def getQuantidadeProduto(self, prod_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT count(1) cont FROM venda_carrinho where produto_id= %s", [prod_id])
        row = dictfetchall(cursor)
        if row[0]['cont'] == 0:
            quantidade = 1
        else:
            cursor.execute("SELECT (quantidade + 1) quantidade FROM venda_carrinho where produto_id = %s", [prod_id])
            row = dictfetchall(cursor)
            quantidade = row[0]['quantidade']
        class Meta:
            model = Produto
            fields = ['quantidade']
    return quantidade

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def getViewCarrinho(user_id, request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM View_Carrinho where user_id = %s order by id", [user_id])
        row = dictfetchall(cursor)
        class Meta:
            model = View_Carrinho
            fields = ['id', 'user_id', 'produto_id', 'nome', 'quantidade', 'valor_unitario', 'valor_total', 'qt_itens']
    return row

def removeitem(self, car_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM venda_carrinho WHERE id = %s", [car_id])
        row = cursor.fetchone()
        return row
    
def limparItensCarrinho(self, user_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM venda_carrinho WHERE user_id = %s", [user_id])
        row = cursor.fetchone()
    return row

def getViewPedidos(user_id, self):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM View_Pedido WHERE user_id = %s ORDER BY id", [user_id])
        row = dictfetchall(cursor)
        class Meta:
            model = View_Pedido
            fields = ['id', 'user_id' 'nr_pedido', 'produto_id', 'nome', 'quantidade', 'valor_unitario', 'valor_total']
        return row