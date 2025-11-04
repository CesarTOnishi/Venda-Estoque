from django.urls import path
from . import views

urlpatterns = [
    path('relatorio/', views.relatorio, name='relatorio'),
    path('relatoriovendas/', views.relatoriovendas, name='relatoriovendas'),
    path('relatorioEstoque/', views.relatorioestoque, name='relatorioestoque'),
    path('relatorioporcliente/', views.relatoriovendacliente, name='relatoriovendacliente'),
    path("relatoriovendapagamento/", views.relatoriovendapagamento, name="relatoriovendapagamento"),
    path("relatoriofornecedores/", views.relatoriofornecedores, name="relatoriofornecedores"),
    path('autocomplete-fornecedor/', views.autocomplete_fornecedor, name='autocomplete_fornecedor'),
    path('relatoriocontas/', views.relatoriocontas, name='relatoriocontas'),
    path("relatoriocompras/", views.relatoriocompras, name="relatoriocompras"),
    path('relatorioextrato/', views.relatorioextrato, name='relatorioextrato'),
    path('clientes_json/', views.clientes_json, name='clientes_json'),

]