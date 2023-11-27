from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.tela, name='tela'),
    path('estoque/', views.estoque, name='estoque'),
    path('lista/', views.lista, name='lista'),
    path('editar/<int:prod_id>', views.editar, name='editar'),
    path('salvar/<int:prod_id>/', views.salvar, name='salvar'),
    path('remover/<int:prod_id>', views.remover, name='remover'),
    path('filtro/', views.filtro, name="filtro"),
    path('', include('venda.urls')),

]