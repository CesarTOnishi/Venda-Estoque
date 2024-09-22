from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from .models import Cliente
from datetime import date
from django.contrib.auth.decorators import login_required
from cliente.functions import removerCliente
from django.contrib import messages
import re

@login_required(login_url="/login/")
def clientes(request):
    clientes = Cliente.objects.all()
    context = {
        'clientes': clientes
    }
    return render(request, 'cliente.html', context)

@login_required(login_url="/login/")
def cadastrocliente(request):
    return render(request, 'cadastrocliente.html')

@login_required(login_url="/login/")
def cadcli(request):
    if request.method == "POST":
        nome = request.POST.get('nome')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        cpf = request.POST.get('cpf')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        data_nascimento_str = request.POST.get('data_nascimento')

        errors = []


        if not nome:
            errors.append("O nome é obrigatório.")
        if not cidade:
            errors.append("A cidade é obrigatória.")
        if not estado:
            errors.append("O estado é obrigatório.")
        if not cpf:
            errors.append("O CPF é obrigatório")
        if not email:
            errors.append("O email é obrigatório.")
        if not telefone:
            errors.append("O telefone é obrigatório.")
        try:
            data_nascimento = date.fromisoformat(data_nascimento_str) if data_nascimento_str else None
        except ValueError:
            errors.append("A data de nascimento é inválida.")
        
        if not data_nascimento_str:
            errors.append("A data de nascimento é obrigatória.")
        else:
            try:
                data_nascimento = date.fromisoformat(data_nascimento_str)
                if data_nascimento > date.today():
                    errors.append("A data de nascimento não pode ser no futuro.")
            except ValueError:
                errors.append("A data de nascimento é inválida.")

        cpf = re.sub(r'[^\d]', '', cpf)
        telefone = re.sub(r'[^\d]', '', telefone)


        if errors:
            context = {
                'errors': errors,
                'nome': nome,
                'cidade': cidade,
                'estado': estado,
                'cpf': cpf,
                'email': email,
                'telefone': telefone,
                'data_nascimento': data_nascimento_str
            }
            return render(request, 'cadastrocliente.html', context)
        
        cliente = Cliente(
            nome=nome,
            cidade=cidade,
            estado=estado,
            cpf=cpf,
            email=email,
            telefone=telefone,
            data_nascimento=data_nascimento
        )
        cliente.save()
        return redirect('cliente') 

    return render(request, 'cadastrocliente.html')

@login_required(login_url="/login/")
def dellcliente(request, cli_id):
    removerCliente(cli_id)
    clientes = Cliente.objects.all()
    context ={
        'clientes' : clientes
    }
    return render(request, 'cliente.html', context)

@login_required(login_url="/login/")
def confirmardelete(request, cli_id):
    cliente = get_object_or_404(Cliente, id=cli_id)
    
    if request.method == "POST":
        removerCliente(cli_id)
        messages.success(request, "Cliente e pedidos associados foram deletados com sucesso.")
        return redirect('cliente')
    
    context = {
        'cliente': cliente
    }
    return render(request, 'confirmarcliente.html', context)

def editarcliente(request, cli_id):        #O prod_id serve para recuperar o id de alguma coisa
    cliente = Cliente.objects.get(id=cli_id)
    context = { 
        'cliente': cliente
    }
    return render(request, "editarcli.html", context)

@login_required(login_url="/login/")
def editarcli(request, cli_id):
    # Busca o cliente pelo ID
    cliente = Cliente.objects.get(id=cli_id)

    if request.method == 'POST':
        # Coleta os dados enviados no formulário
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        cpf = request.POST.get('cpf').replace('.', '').replace('-', '')  # Limpa CPF
        email = request.POST.get('email')
        telefone = request.POST.get('telefone').replace('(', '').replace(')', '').replace(' ', '').replace('-', '')  # Limpa Telefone
        data_nascimento_str = request.POST.get('data_nascimento')

        errors = []

        # Validações dos campos
        if not cidade:
            errors.append("A cidade é obrigatória.")
        if not estado:
            errors.append("O estado é obrigatório.")
        if not cpf:
            errors.append("O CPF é obrigatório.")
        if not email:
            errors.append("O email é obrigatório.")
        if not telefone:
            errors.append("O telefone é obrigatório.")
        
        # Validação da data de nascimento
        try:
            data_nascimento = date.fromisoformat(data_nascimento_str) if data_nascimento_str else None
            if data_nascimento and data_nascimento > date.today():
                errors.append("A data de nascimento não pode ser no futuro.")
        except ValueError:
            errors.append("A data de nascimento é inválida.")
        
        if not data_nascimento_str:
            errors.append("A data de nascimento é obrigatória.")

        # Se houver erros, renderiza o template de volta com os erros
        if errors:
            context = {
                'errors': errors,
                'cliente': cliente,
                'cidade': cidade,
                'estado': estado,
                'cpf': cpf,
                'email': email,
                'telefone': telefone,
                'data_nascimento': data_nascimento_str
            }
            return render(request, 'editarcli.html', context)

        # Atualizando os dados do cliente
        cliente.cidade = cidade
        cliente.estado = estado
        cliente.cpf = cpf
        cliente.email = email
        cliente.telefone = telefone
        cliente.data_nascimento = data_nascimento
        cliente.save()

        return redirect('cliente')

    # Se for uma requisição GET, renderiza o formulário preenchido com os dados do cliente
    context = {
        'cliente': cliente,
        'cidade': cliente.cidade,
        'estado': cliente.estado,
        'cpf': cliente.cpf,
        'email': cliente.email,
        'telefone': cliente.telefone,
        'data_nascimento': cliente.data_nascimento
    }
    return render(request, 'editarcli.html', context)