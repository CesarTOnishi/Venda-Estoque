from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect

def redirect_to_login(request):
    return redirect('/login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_login),
    path('', include('usuarios.urls')),
    path('auth/', include('estoque.urls')),
    path('venda/', include('venda.urls')),
    path('cliente/', include('cliente.urls')),
    path('compras/', include('compras.urls')),
    path('relatorio/', include('relatorio.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('funcionario/', include('funcionario.urls')),
    path('condicaoPagamento/', include('condicaoPagamento.urls'))
]