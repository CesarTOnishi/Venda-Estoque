from django.contrib import admin

from.models import Cliente

class ClienteAdmin(admin.ModelAdmin):
    model: Cliente
    list_display= ['nome', 'cidade', 'cpf', 'email', 'telefone', 'data_nascimento']
    search_fields= ['nome']
    save_on_top = True

admin.site.register(Cliente, ClienteAdmin)
