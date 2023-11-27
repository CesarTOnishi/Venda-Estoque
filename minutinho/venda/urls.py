from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('addCarrinho/<int:prod_id>/', views.addCarrinho, name="addCarrinho"),
    path('sacola/', views.sacola, name='sacola'),
    path('dellcarrinho/<int:car_id>', views.dellcarrinho, name='dellcarrinho'),
    path('realizarPedido/<int:user_id>/', views.realizarPedido, name='realizarPedido'),
    path('meuspedidos/', views.meuspedidos, name='meuspedidos')
]