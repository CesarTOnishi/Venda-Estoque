from django.db import connection,  transaction
from django.shortcuts import render, redirect
from estoque.models import Produto
from venda.models import Carrinho, View_Carrinho, Pedido, View_Pedido
from venda.functions import getQuantidadeProduto, getViewCarrinho, removeitem, limparItensCarrinho, getViewPedidos, getQuantidadeTotalCarrinho
from django.db.models import Sum, Max
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from cliente.models import Cliente
from django.utils import timezone
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from django.shortcuts import get_object_or_404
from django.conf import settings



@login_required(login_url="/login/")
def catalogo(request):
    user_id = request.user.id
    quantidade_total = getQuantidadeTotalCarrinho(user_id)  # Use a função correta para obter a quantidade total
    produtos = Produto.objects.all().order_by("nome")
    context = {
        'produtos': produtos,
        'quantidade_total': quantidade_total,  # Passe a quantidade total para o template
    }
    return render(request, 'catalogo.html', context)

def addCarrinho(request, prod_id):
    user_id = request.user.id
    produto = Produto.objects.get(id=prod_id)
    quantidade = getQuantidadeProduto(prod_id)

    if produto.estoque < quantidade:
        mensagem = "Estoque insuficiente."
        produtos = Produto.objects.all().order_by("nome")
        quantidade_total = getQuantidadeTotalCarrinho(user_id)
        context = {
            'produtos': produtos,
            'mensagem': mensagem,
            'quantidade_total': quantidade_total,
        }
        return render(request, "catalogo.html", context)
    
    try:
        carrinho = Carrinho.objects.get(produto_id=prod_id, user_id=user_id)
        carrinho.quantidade += quantidade
        carrinho.valor_total = carrinho.valor_unitario * carrinho.quantidade
        carrinho.save()  
    except Carrinho.DoesNotExist:
        carrinho = Carrinho(
            user_id=user_id,
            produto_id=prod_id,
            quantidade=quantidade,
            valor_unitario=produto.preco,
            valor_total=produto.preco * quantidade
        )
        carrinho.save() 

    quantidade_total = getQuantidadeTotalCarrinho(user_id)
    
    mensagem = f"{produto.nome} Adicionado ao carrinho"
    produtos = Produto.objects.all().order_by("nome")
    context = {
        'produtos': produtos,
        'mensagem': mensagem,
        'quantidade_total': quantidade_total,
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

@login_required(login_url="/login/")
def sacola(request):
    user_id = request.user.id
    results = Cliente.objects.all()
    viewCarrinho = getViewCarrinho(user_id, request)
    valor_geral = View_Carrinho.objects.filter(user_id=user_id).aggregate(Sum('valor_total')).get('valor_total__sum', 0.00)
    if viewCarrinho:
        mensagem =""
        context ={
            'viewCarrinho': viewCarrinho,
            'user_id': user_id,
            'valor_geral':valor_geral,
            'clientes': results
        }
    else:
        mensagem = "Não existem pedidos no carrinho!"
        context = {
            'user_id': user_id,
            'mensagem': mensagem,
            'valor_geral':valor_geral,
            'clientes': results
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

def realizarPedido(request):
    if request.method == "POST":
        user_id = request.user.id
        cliente_id = request.POST.get('cliente_id')

        if not cliente_id:
            mensagem = "Selecione um cliente válido." 
            viewCarrinho = getViewCarrinho(user_id, request)
            context ={
                'mensagem': mensagem,
                'viewCarrinho':viewCarrinho
            }
            return render(request, 'sacola.html', context)

        try:
            cliente_id = int(cliente_id)  # Converte o cliente_id para inteiro
            cliente = Cliente.objects.get(id=cliente_id)
        except (ValueError, Cliente.DoesNotExist):
            mensagem = "Cliente não encontrado."
            viewCarrinho = getViewCarrinho(user_id, request)
            context = {
                'mensagem': mensagem,
                'viewCarrinho':viewCarrinho
            }
            return render(request, 'sacola.html', context)

        carrinho = getViewCarrinho(user_id, request)

        if not carrinho:
            mensagem = "Carrinho vazio. Adicione itens ao carrinho antes de realizar um pedido."
            context = {
                'mensagem':mensagem
            }
            return render(request, 'sacola', context)

        max_nr_pedido = Pedido.objects.filter(user_id=user_id).aggregate(Max('nr_pedido'))
        ultimo_nr_pedido = max_nr_pedido['nr_pedido__max'] or 0

        try:
            with transaction.atomic():
                for car in carrinho:
                    produto = Produto.objects.get(id=car['produto_id'])
                    if produto.estoque < car['quantidade']:
                        mensagem = f"Estoque insuficiente para o produto {produto.nome}"
                        viewCarrinho = getViewCarrinho(user_id, request)
                        context ={
                            'mensagem': mensagem,
                            'viewCarrinho':viewCarrinho
                        }
                        return render(request, 'sacola.html', context)

                    pedido = Pedido(
                        nr_pedido=ultimo_nr_pedido + 1,
                        user_id=user_id,
                        cliente=cliente, 
                        produto_id=car['produto_id'],
                        quantidade=car['quantidade'],
                        valor_unitario=car['valor_unitario'],
                        valor_total=car['valor_total'],
                        data_pedido=timezone.now()
                    )
                    pedido.save()

                    produto.estoque -= car['quantidade']
                    produto.save()

                limparItensCarrinho(request, user_id)
            return redirect('sacola')

        except ValueError as e:
            messages.error(request, str(e))
            return redirect('sacola')
        except Exception as e:
            messages.error(request, f"Erro inesperado: {str(e)}")
            return redirect('sacola')

    else:
        return redirect('sacola')


@login_required(login_url="/login/")
def meuspedidos(request):
    user_id = request.user.id
    viewPedidos = getViewPedidos(user_id, request)
    valor_geral = View_Pedido.objects.filter(user_id=user_id).aggregate(Sum('valor_total')).get('valor_total__sum', 0.00)
    
    pedidos = View_Pedido.objects.all()
    
    pedidos_dict = {} 
    
    for pedido in pedidos:
        nr_pedido = pedido.nr_pedido
        if nr_pedido not in pedidos_dict:
            pedidos_dict[nr_pedido] = {
                'data_pedido': pedido.data_pedido,
                'itens': [],
                'cliente_nome': pedido.cliente_nome,
                'id': pedido.id 
            }
        
        pedidos_dict[nr_pedido]['itens'].append(pedido)
    
    context = {
        'viewPedidos': viewPedidos,
        'valor_geral': valor_geral,
        'pedidos_dict': pedidos_dict  
    }
    
    return render(request, "meuspedidos.html", context)

def gerarpdf(request, ped_id):
    pedido = get_object_or_404(Pedido, id=ped_id)
    cliente = get_object_or_404(Cliente, id=pedido.cliente_id)
    itens = Pedido.objects.filter(nr_pedido=pedido.nr_pedido)
    
    quantidade_total = 0
    itens_detalhados = []
    for item in itens:
        produto = Produto.objects.filter(id=item.produto_id).first() 
        if produto:
            itens_detalhados.append({
                'produto_id': item.produto_id,
                'nome': produto.nome,
                'quantidade': item.quantidade,
                'valor_unitario': item.valor_unitario,
                'valor_total': item.valor_total
            })
            quantidade_total += item.quantidade

        else:
            itens_detalhados.append({
                'produto_id': item.produto_id,
                'nome': 'Produto não encontrado',
                'quantidade': item.quantidade,
                'valor_unitario': item.valor_unitario,
                'valor_total': item.valor_total
            })

    total_geral = sum(item['valor_total'] for item in itens_detalhados)
    
    # Carrega o template HTML para o PDF
    template = get_template('pdfpedido.html')
    context = {
        'pedido': pedido,
        'itens': itens_detalhados,
        'total_geral': total_geral,
        'quantidade_total': quantidade_total,
        'cliente_nome': cliente.nome,
        'cliente_cidade': cliente.cidade,
        'cliente_estado': cliente.estado,
        'cliente_cpf': cliente.cpf,
        'cliente_email': cliente.email,
        'cliente_telefone': cliente.telefone,
    }
    html = template.render(context)
    
    # Cria um buffer para armazenar o PDF gerado
    result = BytesIO()
    pdf = pisa.CreatePDF(html, dest=result)
    
    if pdf.err:
        return HttpResponse('Erro ao gerar PDF', status=500)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=pedido_{ped_id}.pdf'
    return response