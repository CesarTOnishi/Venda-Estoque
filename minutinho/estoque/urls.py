from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.tela, name='tela'),
    path('estoque/', views.estoque, name='estoque'),
    path('lista/', views.lista, name='lista'),
    path('editar/<int:prod_id>', views.editar, name='editar'),
    path('inicial', views.inicial, name='inicial'),
    path('salvar/<int:prod_id>/', views.salvar, name='salvar'),
    path('remover/<int:prod_id>', views.remover, name='remover'),
    path('venda/', include('venda.urls')),
    path('cliente/', include('cliente.urls')),
    path('fornecedor/', include('fornecedor.urls')),
    path('compras/', include('compras.urls')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]