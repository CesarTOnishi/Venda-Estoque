from django.contrib import admin
from .models import Pedido, Carrinho, View_Pedido

class PedidoAdmin(admin.ModelAdmin):
    model = Pedido
    list_display = ['nr_pedido', 'user_id', 'produto_id', 'quantidade', 'valor_unitario', 'valor_total']
    search_fields = ['nr_pedido', 'user_id']
    save_on_top = True

admin.site.register(Pedido, PedidoAdmin)

class CarrinhoAdmin(admin.ModelAdmin):
    model = Carrinho
    list_display = ['user_id', 'produto_id', 'quantidade', 'valor_unitario', 'valor_total']
    search_fields = ['user_id', 'produto_id']
    save_on_top = True

admin.site.register(Carrinho, CarrinhoAdmin)

class View_PedidoAdmin(admin.ModelAdmin):
    model = View_Pedido
    list_display = ['produto_id', 'id', 'user_id', 'nr_pedido', 'nome', 'quantidade', 'valor_unitario', 'valor_total', 'cliente_nome']
    search_fields = ['nr_pedido', 'user_id', 'nome']
    save_on_top = True

admin.site.register(View_Pedido, View_PedidoAdmin)