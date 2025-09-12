from django.urls import path
from . import views

urlpatterns = [
    path('relatorio/', views.relatorio, name='relatorio'),
    path('maisvendido/', views.relatoriovenda, name='relatoriovenda'),
    path('relatorioEstoque/', views.relatorioestoque, name='relatorioestoque'),
    path("relatoriocliente/", views.relatorioclientes, name="relatorioclientes"),
    path("relatoriofuncionarios/", views.relatoriofuncionarios, name="relatoriofuncionarios"),
    path("relatoriovendapagamento/", views.relatoriovendapagamento, name="relatoriovendapagamento"),
    path("relatoriofornecedores/", views.relatoriofornecedores, name="relatoriofornecedores"),
    path('autocomplete-fornecedor/', views.autocomplete_fornecedor, name='autocomplete_fornecedor'),
    path('relatoriocontas/', views.relatoriocontas, name='relatoriocontas'),
    path('relatorioextrato/', views.relatorioextrato, name='relatorioextrato'),


]