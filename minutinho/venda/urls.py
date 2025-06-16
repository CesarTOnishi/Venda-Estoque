from django.urls import include, path
from . import views
from .views import gerarpdf, api_condicoes_pagamento

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('addCarrinho/<int:prod_id>/', views.addCarrinho, name="addCarrinho"),
    path('sacola/', views.sacola, name='sacola'),
    path('dellcarrinho/<int:car_id>', views.dellcarrinho, name='dellcarrinho'),
    path('realizarPedido/', views.realizarPedido, name='realizarPedido'),
    path('meuspedidos/', views.meuspedidos, name='meuspedidos'),
    path('pedido/<int:ped_id>/pdf/', gerarpdf, name='gerarpdf'),
    path('api/condicoes-pagamento/', api_condicoes_pagamento, name='api_condicoes_pagamento'),

]