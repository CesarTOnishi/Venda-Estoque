from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.tabelaFuncionarios, name='tabelaFuncionarios'),
]