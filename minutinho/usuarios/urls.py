from django.urls import include, path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('', views.login, name="login"),
    path('tela/', include('estoque.urls')),
]