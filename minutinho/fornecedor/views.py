from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from .models import Fornecedor
from datetime import date
from django.contrib.auth.decorators import login_required
from fornecedor.functions import removerFornecedor
from django.contrib import messages
import re

@login_required(login_url="/login/")
def fornecedor(request):
    fornecedores = Fornecedor.objects.all()
    context = {
        'fornecedores': fornecedores
    }
    return render(request, 'fornecedor.html', context)

@login_required(login_url="/login/")
def cadastrofornecedor(request):
    return render(request, 'cadastrofornecedor.html')

@login_required(login_url="/login/")
def cadfor(request):
    if request.method == "POST":
        tipo_pessoa = request.POST.get('tipo_pessoa')
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        cnpj = request.POST.get('cnpj')
        endereco = request.POST.get('endereco')
        estado = request.POST.get('estado')
        cidade = request.POST.get('cidade')
        numero = request.POST.get('numero')

        errors = []

        cnpj = re.sub(r'[^\d]', '', cnpj)
        cpf = re.sub(r'[^\d]', '', cpf)

        if not tipo_pessoa:
            errors.append("O tipo de pessoa é obrigatório.")
        if tipo_pessoa == "Pessoa Física" and not cpf:
            errors.append("O CPF é obrigatório para Pessoa Física.")
        if tipo_pessoa == "Pessoa Jurídica" and not cnpj:
            errors.append("O CNPJ é obrigatório para Pessoa Jurídica.")
        if not nome:
            errors.append("O nome é obrigatório.")
        if not endereco:
            errors.append("O endereço é obrigatório.")
        if not cidade:
            errors.append("A cidade é obrigatória.")
        if not estado:
            errors.append("O estado é obrigatório.")
        if not numero:
            errors.append("O número é obrigatório.")
        else:
            try:
                numero = int(numero)
                if numero < 0:
                    errors.append("O número não pode ser negativo.")
            except ValueError:
                errors.append("O número deve ser um valor numérico.")
        
        if tipo_pessoa == "Pessoa Jurídica" and len(cnpj) != 14:
            errors.append("O CNPJ deve ter 14 dígitos.")
        if tipo_pessoa == "Pessoa Física" and len(cpf) != 11:
            errors.append("O CPF deve ter 11 dígitos.")
        
        if tipo_pessoa == "Pessoa Física" and Fornecedor.objects.filter(cpf=cpf).exists():   # Filter Faz uma pesquisa no banco de dados/(cpf)faz a pesquisa no modello cpf
            errors.append("Este CPF já está cadastrado.") #e o exist faz verifica se sexiste e volta o valor boleano.
        
        if tipo_pessoa == "Pessoa Jurídica" and Fornecedor.objects.filter(cnpj=cnpj).exists():
            errors.append("Este CNPJ já está cadastrado.")

        if errors:
            context = {
                'tipo_pessoa': tipo_pessoa,
                'errors': errors,
                'nome': nome,
                'endereco': endereco,
                'cidade': cidade,
                'estado': estado,
                'cnpj': cnpj,
                'cpf': cpf,
                'numero': numero,
            }
            return render(request, 'cadastrofornecedor.html', context)
        
        fornecedor = Fornecedor(
            tipo_pessoa=tipo_pessoa,
            nome=nome,
            endereco=endereco,
            cidade=cidade,
            estado=estado,
            cnpj=cnpj if tipo_pessoa == "Pessoa Jurídica" and cnpj else None,
            cpf=cpf if tipo_pessoa == "Pessoa Física" and cpf else None,
            numero=numero,
        )
        fornecedor.save()

        return redirect('fornecedor')

    return render(request, 'cadastrofornecedor.html')


@login_required(login_url="/login/")
def dellfornecedor(request, forn_id):
    removerFornecedor(forn_id)
    fornecedores = Fornecedor.objects.all()
    context ={
        'fornecedores' : fornecedores
    }
    return render(request, 'fornecedor.html', context)

def editarfornecedor(request, forn_id):        #O prod_id serve para recuperar o id de alguma coisa
    fornecedor = Fornecedor.objects.get(id=forn_id)
    context = { 
        'fornecedor': fornecedor
    }
    return render(request, "editarfornecedor.html", context)

@login_required(login_url="/login/")
def editarforn(request, forn_id):
    fornecedor = get_object_or_404(Fornecedor, id=forn_id)
    
    if request.method == "POST":
        tipo_pessoa = request.POST.get('tipo_pessoa')
        endereco = request.POST.get('endereco')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        numero = request.POST.get('numero')
        cnpj = request.POST.get('cnpj')
        cpf = request.POST.get('cpf')

        errors = []

        cnpj = re.sub(r'[^\d]', '', cnpj) if cnpj else None
        cpf = re.sub(r'[^\d]', '', cpf) if cpf else None

        if not tipo_pessoa:
            errors.append("O tipo de pessoa é obrigatório.")
        if tipo_pessoa == "Pessoa Física" and not cpf:
            errors.append("O CPF é obrigatório para Pessoa Física.")
        if tipo_pessoa == "Pessoa Jurídica" and not cnpj:
            errors.append("O CNPJ é obrigatório para Pessoa Jurídica.")
        if not endereco:
            errors.append("O endereço é obrigatório.")
        if not cidade:
            errors.append("A cidade é obrigatória.")
        if not estado:
            errors.append("O estado é obrigatório.")
        if not numero:
            errors.append("O número é obrigatório.")
        else:
            try:
                numero = int(numero)
                if numero < 0:
                    errors.append("O número não pode ser negativo.")
            except ValueError:
                errors.append("O número deve ser um valor numérico.")
        if tipo_pessoa == "Pessoa Jurídica" and cnpj and len(cnpj) != 14:
            errors.append("O CNPJ deve ter 14 dígitos.")
        if tipo_pessoa == "Pessoa Física" and cpf and len(cpf) != 11:
            errors.append("O CPF deve ter 11 dígitos.")

        if tipo_pessoa == "Pessoa Física" and cpf:
            if Fornecedor.objects.filter(cpf=cpf).exclude(id=fornecedor.id).exists():
                errors.append("Já existe um fornecedor com este CPF.")
        
        if tipo_pessoa == "Pessoa Jurídica" and cnpj:
            if Fornecedor.objects.filter(cnpj=cnpj).exclude(id=fornecedor.id).exists():
                errors.append("Já existe um fornecedor com este CNPJ.")


        if errors:
            context = {
                'errors': errors,
                'fornecedor': fornecedor
            }
            return render(request, 'editarfornecedor.html', context)

        fornecedor.tipo_pessoa = tipo_pessoa
        fornecedor.endereco = endereco
        fornecedor.cidade = cidade
        fornecedor.estado = estado
        fornecedor.numero = numero
        fornecedor.cnpj = cnpj if tipo_pessoa == "Pessoa Jurídica" else None
        fornecedor.cpf = cpf  if tipo_pessoa == "Pessoa Física" else None
        fornecedor.save()
        return redirect('fornecedor')

    return render(request, 'editarfornecedor.html', {'fornecedor': fornecedor})

def confirmardell(request, forn_id):
    fornecedor = get_object_or_404(Fornecedor, id=forn_id)
    
    if request.method == "POST":
        removerFornecedor(forn_id)
        messages.success(request, "Fornecedor e pedidos associados foram deletados com sucesso.")
        return redirect('fornecedor')
    
    context = {
        'fornecedor': fornecedor
    }
    return render(request, 'confirmarfornecedor.html', context)