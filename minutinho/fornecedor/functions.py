from django.db import models, connection
from fornecedor.models import Fornecedor

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def removerFornecedor(forn_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM fornecedor_fornecedor WHERE id = %s", [forn_id])
    except Exception as e:
        print(f"Erro ao remover fornecedor: {e}")