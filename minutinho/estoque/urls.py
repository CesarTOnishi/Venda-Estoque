from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.tela, name='tela'),
    path('estoque/', views.estoque, name='estoque'),
    path('lista/', views.lista, name='lista'),
    path('editarProd/<int:prod_id>', views.editarProd, name='editarProd'),
    path('inicial', views.inicial, name='inicial'),
    path('salvar/<int:prod_id>/', views.salvar, name='salvar'),
    path('removerProd/<int:prod_id>', views.removerProd, name='removerProd'),
    path('venda/', include('venda.urls')),
    path('cliente/', include('cliente.urls')),
    path('fornecedor/', include('fornecedor.urls')),
    path('funcionario/', include('funcionario.urls')),
    path('compras/', include('compras.urls')),
    path('relatorio/', include('relatorio.urls')),
    path('condicaoPagamento/', include('condicaoPagamento.urls')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('categoria/', views.categoria, name='categoria'),
    path('cadastroCategoria/', views.cadastroCategoria, name='cadastroCategoria'),
    path('cadcat/', views.cadcat, name='cadcat'),
    path('editCategoria/<int:cat_id>/', views.editCategoria, name='editCategoria'),
    path('editarCategoria/<int:cat_id>/', views.editarCategoria, name='editarCategoria'),
    path('deletarCategoria/<int:cat_id>/', views.deletarCategoria, name='deletarCategoria'),

]