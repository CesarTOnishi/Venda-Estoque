from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.clientes, name='cliente'),
    path('cadastro/', views.cadastrocliente, name='cadastrocliente'),
    path('cad/', views.cadcli, name='cadcli'),
    path('deletar/<int:cli_id>/', views.dellcliente, name='dellcliente'),
    path('confirmardelete/<int:cli_id>', views.confirmardelete, name='confirmardelete'),
    path('editarcli/<int:cli_id>', views.editarcliente, name='editarcliente'),
    path('salvarcli/<int:cli_id>', views.editarcli, name='editarcli'),
]