from decimal import Decimal, InvalidOperation

from django.http import HttpResponse
from .functions import deletarProduto
from django.shortcuts import render, redirect
from .models import Produto

def estoque(request):
    if request.method =="GET":
        return render(request, 'addprodutos.html')
    else:
        nome = request.POST.get('nome')
        estoque = request.POST.get('estoque')
        descricao = request.POST.get('descricao')
        preco = request.POST.get('preco')

        produto = Produto(nome=nome, estoque=estoque, descricao=descricao, preco=preco)
        produto.save()
        return redirect('lista') 
    
def tela(request):
    return render(request, 'tela.html')

def lista(request):

    produtos = Produto.objects.all().order_by('nome')
    context = {
        'produtos': produtos
    }
    return render(request, 'lista.html', context)

def editar(request, prod_id):        #O prod_id serve para recuperar o id de alguma coisa
    produto = Produto.objects.get(id=prod_id)
    context = { 
        'produto': produto
    }
    return render(request, "editar.html", context)

def remover(request, prod_id):
    delete = deletarProduto(prod_id)
    produtos = Produto.objects.all().order_by("nome")
    context ={
        'produtos' : produtos
    }
    return render(request, 'lista.html', context)

def salvar(request, prod_id):
    produto = Produto.objects.get(id=prod_id)
    nome = request.POST.get('nome')
    estoque = request.POST.get('estoque')
    descricao = request.POST.get('descricao')
    preco = request.POST.get('preco')

    try:
        preco_dec = Decimal(preco.replace(",", "."))
    except InvalidOperation:
        return HttpResponse("Preço inválido")
        
    produto.preco = preco_dec
    produto.nome = nome
    produto.estoque = estoque
    produto.descricao = descricao
    produto.save()
    return redirect('lista')

def filtro(request):
    palavra = request.POST.get("palavra")
    produtos = Produto.objects.filter(nome__contains=palavra)
    context = {
        'produtos': produtos
    }
    return render(request,'lista.html', context)