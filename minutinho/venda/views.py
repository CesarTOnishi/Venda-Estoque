from django.db import connection,  transaction
from django.shortcuts import render, redirect
from estoque.models import Produto
from venda.models import Carrinho, View_Carrinho, Pedido, View_Pedido
from venda.functions import getQuantidadeProduto, getViewCarrinho, removeitem, limparItensCarrinho, getViewPedidos
from django.db.models import Sum, Max


def catalogo(request):
    user_id = request.user.id
    viewCarrinho = getViewCarrinho(user_id, request)
    produtos = Produto.objects.all().order_by("nome")
    context = {
        'produtos': produtos,
        'viewCarrinho': viewCarrinho,
    }
    return render(request, 'catalogo.html', context)

def addCarrinho(request, prod_id):
    user_id = request.user.id
    produto = Produto.objects.get(id=prod_id)
    quantidade = getQuantidadeProduto(request, prod_id)
    if quantidade == 1:
        carrinho = Carrinho()
    else:
        carrinho = Carrinho.objects.get(produto_id=prod_id)
    carrinho.user_id = user_id
    carrinho.produto_id = prod_id
    carrinho.quantidade = quantidade
    carrinho.valor_unitario = produto.preco
    carrinho.valor_total = produto.preco * quantidade
    carrinho.save()
    mensagem = produto.nome + " Adicionado ao carrinho"
    produtos = Produto.objects.all().order_by("nome")
    context = {
        'produtos': produtos,
        'mensagem': mensagem,
    }
    return render(request, "catalogo.html", context)

def viewCarrinho(request):
    user_id = request.user.id
    viewCarrinho = getViewCarrinho(user_id, request)
    context={
        'viewCarrinho': viewCarrinho,
        'user_id': user_id
    }
    return render(request, 'addCarrinho/<int:prod_id>/', context)

def sacola(request):
    user_id = request.user.id
    viewCarrinho = getViewCarrinho(user_id, request)
    valor_geral = View_Carrinho.objects.filter(user_id=user_id).aggregate(Sum('valor_total')).get('valor_total__sum', 0.00)
    if viewCarrinho:
        mensagem =""
        context ={
            'viewCarrinho': viewCarrinho,
            'user_id': user_id,
            'valor_geral':valor_geral
        }
    else:
        mensagem = "Não existem pedidos no carrinho!"
        context = {
            'user_id': user_id,
            'mensagem': mensagem,
        }
    return render(request, 'sacola.html', context)

def dellcarrinho(request, car_id):
    user_id = request.user.id
    removeitem(request, car_id)
    valor_geral = View_Carrinho.objects.filter(user_id=user_id).aggregate(Sum('valor_total')).get('valor_total__sum', 0.00)
    viewCarrinho = getViewCarrinho(user_id, request)
    context = {
        'viewCarrinho': viewCarrinho,
        'valor_geral': valor_geral,
    }
    return render(request, 'sacola.html', context)

def realizarPedido(request, user_id):
    carrinho = getViewCarrinho(user_id, request)

    max_nr_pedido = Pedido.objects.filter(user_id=user_id).aggregate(Max('nr_pedido'))
    ultimo_nr_pedido = max_nr_pedido['nr_pedido__max'] or 0
    with transaction.atomic():
        
        for car in carrinho:
            pedido = Pedido()
            pedido.nr_pedido = ultimo_nr_pedido + 1
            pedido.user_id = car['user_id']
            pedido.produto_id = car['produto_id']
            pedido.quantidade = car['quantidade']
            pedido.valor_unitario = car['valor_unitario']
            pedido.valor_total = car['valor_total']
            pedido.save()
        limparCarrinho = limparItensCarrinho(request, user_id)
    return render(request, 'tela.html')

def meuspedidos(request):
    user_id = request.user.id
    viewPedidos = getViewPedidos(user_id, request)
    valor_geral = View_Pedido.objects.filter(user_id=user_id).aggregate(Sum('valor_total')).get('valor_total__sum', 0.00)
    
    # Agora, buscamos os pedidos do modelo Pedido
    pedidos = View_Pedido.objects.all()
    
    pedidos_dict = {}  # Um dicionário para organizar os pedidos
    
    for pedido in pedidos:
        nr_pedido = pedido.nr_pedido
        if nr_pedido not in pedidos_dict:
            pedidos_dict[nr_pedido] = []
        
        pedidos_dict[nr_pedido].append(pedido)
    
    context = {
        'viewPedidos': viewPedidos,
        'valor_geral': valor_geral,
        'pedidos_dict': pedidos_dict  # Adicionamos o dicionário de pedidos ao contexto
    }
    
    return render(request, "meuspedidos.html", context)