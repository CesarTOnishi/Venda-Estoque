from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.fornecedor, name='fornecedor'),
    path('cadastro/', views.cadastrofornecedor, name='cadastrofornecedor'),
    path('cad/', views.cadfor, name='cadfor'),
    path('deletar/<int:forn_id>/', views.dellfornecedor, name='dellfornecedor'),
    path('confirmardell/<int:forn_id>', views.confirmardell, name='confirmardell'),
    path('editarforn/<int:forn_id>', views.editarfornecedor, name='editarfornecedor'),
    path('salvarfornecedor/<int:forn_id>', views.editarforn, name='editarforn'),
]