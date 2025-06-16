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
]