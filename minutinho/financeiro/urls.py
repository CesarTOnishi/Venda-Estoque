from django.urls import include, path
from . import views 
from .views import financeiro, atualizarPagamento, atualizarSaldo, atualizarPagamentoPagar

urlpatterns = [
    path('', views.financeiro, name='financeiro'),
    path('contasReceber', views.contasReceber, name='contasReceber'),
    path('contasPagar/', views.contasPagar, name='contasPagar' ),
    path('atualizarPagamento/<int:conta_id>/', atualizarPagamento, name='atualizarPagamento'),
    path('atualizarPagamentoPagar/<int:conta_id>/', atualizarPagamentoPagar, name='atualizarPagamentoPagar'),
    path('atualizarSaldo/<int:conta_id>/', atualizarSaldo, name='atualizarSaldo'),
    path('detalhes-conta/<str:tipo_conta>/<int:conta_id>/', views.detalhes_conta, name='detalhes_conta'),
    path('contaBancaria/', views.contaBancaria, name='contaBancaria'),
    path('contaBancaria/deletar/<int:id>/', views.deletarConta, name='deletarConta'),
    path('contaBancaria/alternar/<int:id>/', views.alternarAtivo, name='alternarAtivo'),
    path('movimento/<conta_id>', views.movimentacoes, name='movimentacoes'),
    path('relatorio/', views.relatorioConta, name='relatorioConta'),

]