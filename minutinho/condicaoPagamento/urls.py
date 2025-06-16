from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.condicaoPagamento, name='condicaoPagamento'),
    path('filtroPagamento/', views.filtroPagamento, name='filtroPagamento'),

]