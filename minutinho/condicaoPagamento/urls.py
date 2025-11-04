from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.condicaoPagamento, name='condicaoPagamento'),
    path('filtroPagamento/', views.filtroPagamento, name='filtroPagamento'),
    path('deletar/<int:condicao_id>/', views.deletarCondicao, name='deletarCondicao'),
    path('relatoriocondicao/', views.relatorioCondicao, name='relatorioCondicao')
]