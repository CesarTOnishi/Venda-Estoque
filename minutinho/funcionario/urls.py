from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.tabelaFuncionarios, name='tabelaFuncionarios'),
    path('funcionarios/deletar/<int:funcionario_id>/', views.deletarFuncionario, name='deletarFuncionario'),
    path("relatoriofuncionarios/", views.relatoriofuncionarios, name="relatoriofuncionarios"),
]