from django.db import migrations, models
import django.db.models.deletion

def remove_views(apps, schema_editor):
    """Remove todas as views problemáticas"""
    schema_editor.execute("DROP VIEW IF EXISTS View_Carrinho;")
    schema_editor.execute("DROP VIEW IF EXISTS View_Pedido;")

def recreate_views(apps, schema_editor):
    """Recria todas as views após as alterações"""
    # View_Carrinho
    schema_editor.execute("""
        CREATE VIEW View_Carrinho AS
        SELECT 
            prod.id AS produto_id,
            car.id,
            car.user_id,
            prod.nome,
            car.quantidade,
            car.valor_unitario,
            car.valor_total,
            qtd.qt_itens,
            prod.estoque
        FROM 
            estoque_produto prod,
            venda_carrinho car,
            (
                SELECT user_id, COUNT(1) AS qt_itens
                FROM venda_carrinho
                GROUP BY user_id
            ) qtd
        WHERE 
            prod.id = car.produto_id
            AND car.user_id = qtd.user_id
        GROUP BY 
            produto_id, car.id, car.user_id, prod.nome, car.quantidade, 
            car.valor_unitario, car.valor_total, prod.estoque
    """)
    
    
    # View_Pedido
    schema_editor.execute("""
        CREATE VIEW View_Pedido AS
        SELECT 
            ped.id AS id,
            prod.id AS produto_id,
            ped.user_id,
            ped.nr_pedido,
            prod.nome AS nome,
            ped.quantidade,
            ped.valor_unitario,
            ped.valor_total,
            ped.data_pedido,
            ped.metodo_pagamento,
            ped.parcelas,
            cli.nome AS cliente_nome
        FROM estoque_produto prod
        JOIN venda_pedido ped ON prod.id = ped.produto_id
        LEFT JOIN cliente_cliente cli ON ped.cliente_id = cli.id
    """)

class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0006_remove_produto_categoria_nome_produto_categoria'),
        ('venda', '0009_pedido_condicao_pagamento'),
    ]

    operations = [
        # 1. Primeiro remove todas as views
        migrations.RunPython(remove_views, migrations.RunPython.noop),
        
        # 2. Faz as alterações dos campos originais
        migrations.AlterField(
            model_name='carrinho',
            name='produto_id',
            field=models.ForeignKey(blank=True, db_column='produto_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='estoque.produto'),
        ),
        migrations.AlterField(
            model_name='pedido',
            name='produto_id',
            field=models.ForeignKey(blank=True, db_column='produto_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='estoque.produto'),
        ),
        
        # 3. Recria todas as views
        migrations.RunPython(recreate_views, migrations.RunPython.noop),
    ]