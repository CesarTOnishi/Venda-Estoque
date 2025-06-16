from django.urls import include, path
from . import views
from .views import notacompra

urlpatterns = [
    path('', views.compra, name='compra'),
    path('criar/', views.criar_pedido, name='criar_pedido'),
    path('fornecedor-autocomplete/', views.fornecedor_autocomplete, name='fornecedor_autocomplete'),
    path('produto-autocomplete/', views.produto_autocomplete, name='produto_autocomplete'),  # Rota para produtos
    path('removercompra/<int:item_id>/', views.removercompra, name='removercompra'),
    path('editar/<int:item_id>/', views.editar, name='editar'),
    path('editar_compra/<int:item_id>/', views.editar_pedido, name='editar_pedido'),
    path('compra/<int:item_id>/pdf/', notacompra, name='notacompra'),

]