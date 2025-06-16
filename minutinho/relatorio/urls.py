from django.urls import path
from . import views

urlpatterns = [
    path('relatorio/', views.relatorio, name='relatorio'),
    path('maisvendido/', views.relatoriovenda, name='relatoriovenda'),
    path('relatorioEstoque/', views.relatorioestoque, name='relatorioestoque'),


]