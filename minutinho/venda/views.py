from django.db import connection,  transaction
from django.shortcuts import render, redirect
from estoque.models import Produto, Categoria
from venda.models import Carrinho, View_Carrinho, Pedido, View_Pedido
from financeiro.models import ContaReceber
from venda.functions import getQuantidadeProduto, getViewCarrinho, removeitem, limparItensCarrinho, getViewPedidos, getQuantidadeTotalCarrinho
from django.db.models import Sum, Max, F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from cliente.models import Cliente
from django.utils import timezone
from django.template.loader import get_template
from django.http import HttpResponse, JsonResponse
from xhtml2pdf import pisa
from io import BytesIO
from django.shortcuts import get_object_or_404
from django.conf import settings
from datetime import timedelta
from condicaoPagamento.models import CondicaoPagamento


@login_required(login_url="/login/")
def catalogo(request):
    user_id = request.user.id
    quantidade_total = getQuantidadeTotalCarrinho(user_id) 
    categoria_filtro = request.GET.get('categoria')
    preco_filtro = request.GET.get('preco_filtro')
    alfabeto_filtro = request.GET.get('alfabeto_filtro')

    if categoria_filtro:
        produtos = Produto.objects.filter(categoria_nome=categoria_filtro).order_by("nome")
    else:
        produtos = Produto.objects.all().order_by("nome")

    if preco_filtro == 'menor':
        produtos = produtos.order_by('preco')  
    elif preco_filtro == 'maior':
        produtos = produtos.order_by('-preco') 

    if alfabeto_filtro == 'asc':
        produtos = produtos.order_by('nome')  
    elif alfabeto_filtro == 'desc':
        produtos = produtos.order_by('-nome')  
        

    categorias = Categoria.objects.all()
    context = {
        'produtos': produtos,
        'quantidade_total': quantidade_total,  
        'categorias': categorias,
        'categoria_filtro': categoria_filtro,
        'preco_filtro': preco_filtro,
        'alfabeto_filtro' : alfabeto_filtro,
    }
    return render(request, 'catalogo.html', context)

def addCarrinho(request, prod_id):
    print("addCarrinho chamado")
    user_id = request.user.id
    produto = get_object_or_404(Produto, id=prod_id)
    quantidade = 1  
    errors = []

    if produto.estoque <= 0:
        errors.append(f"Produto {produto.nome} está esgotado!")
    elif produto.estoque < quantidade:
        errors.append(f"Estoque insuficiente. Máximo disponível: {produto.estoque}")

    if not errors:
        try:
            with transaction.atomic():
                print("Tentando get_or_create")
                carrinho_item, created = Carrinho.objects.get_or_create(
                    produto=produto,
                    user_id=user_id,
                    defaults={
                        'quantidade': quantidade,
                        'valor_unitario': produto.preco,
                        'valor_total': produto.preco * quantidade
                    }
                )

                if not created:
                    nova_quantidade = carrinho_item.quantidade + quantidade
                    if nova_quantidade > produto.estoque:
                        errors.append("Quantidade solicitada excede o estoque disponível")
                    else:
                        carrinho_item.quantidade = nova_quantidade
                        carrinho_item.valor_total = carrinho_item.valor_unitario * nova_quantidade
                        carrinho_item.save()

        except Exception as e:
            errors.append(f"Erro ao adicionar ao carrinho: {str(e)}")

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': not bool(errors),
            'errors': errors,
            'estoque_disponivel': produto.estoque,
            'quantidade_carrinho': Carrinho.objects.filter(
                user_id=user_id, 
                produto_id=prod_id
            ).aggregate(Sum('quantidade'))['quantidade__sum'] or 0,
            'produto_id': prod_id,
            'mensagem': "Item adicionado ao carrinho" if not errors else errors[0]
        })

    if errors:
        messages.error(request, errors[0])
    else:
        messages.success(request, "Item adicionado ao carrinho")
    
    return redirect('catalogo')

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
    tipo_pagamento = dict(CondicaoPagamento.TIPO_PAGAMENTO_CHOICES)
    results = Cliente.objects.all()
    viewCarrinho = getViewCarrinho(user_id, request)
    valor_geral = View_Carrinho.objects.filter(user_id=user_id).aggregate(Sum('valor_total')).get('valor_total__sum') or 0.00
    
    # Pega o método de pagamento selecionado, se existir
    metodo_selecionado = request.GET.get('metodo_pagamento') or request.POST.get('metodo_pagamento')
    
    # Filtra as condições de pagamento com base no método selecionado
    condicoes_pagamento = CondicaoPagamento.objects.filter(ativo=True)
    if metodo_selecionado:
        condicoes_pagamento = condicoes_pagamento.filter(tipo_pagamento=metodo_selecionado)
    
    # Se um método de pagamento for selecionado, tenta pegar a primeira condição de pagamento
    condicao_selecionada = None
    if metodo_selecionado:
        condicao_selecionada = condicoes_pagamento.first()
    
    # Se o formulário foi enviado, pega o ID da condição de pagamento
    if request.method == 'POST':
        condicao_id = request.POST.get('condicao_pagamento_id')
        cliente_id = request.POST.get('cliente_id')

        if condicao_id:
            condicao = get_object_or_404(CondicaoPagamento, id=condicao_id)
            valor_com_desconto = valor_geral * (1 - condicao.desconto / 100)
            valor_final = valor_com_desconto * (1 + condicao.juros / 100)
            valor_parcela = valor_final / condicao.parcelas if condicao.parcelas > 0 else valor_final

            context = {
                'viewCarrinho': viewCarrinho,
                'user_id': user_id,
                'valor_geral': valor_geral,
                'clientes': results,
                'condicoes_pagamento': condicoes_pagamento,
                'condicao_selecionada': condicao,
                'valor_parcela': valor_parcela,
                'valor_final': valor_final,
                'tipo_pagamento': tipo_pagamento,
                'parcelas': condicao.parcelas,
                'metodo_selecionado': metodo_selecionado,
                'cliente_selecionado_id': cliente_id,
            }
            return render(request, 'sacola.html', context)

    # Contexto para a renderização padrão da página
    context = {
        'viewCarrinho': viewCarrinho,
        'user_id': user_id,
        'valor_geral': valor_geral,
        'clientes': results,
        'condicoes_pagamento': condicoes_pagamento,
        'tipo_pagamento': tipo_pagamento,
        'metodo_selecionado': metodo_selecionado,
        'condicao_selecionada': condicao_selecionada,  # Passando a condição selecionada para o template
    }

    if not viewCarrinho:
        errors = ["Não existem pedidos no carrinho!"]
        context['errors'] = errors

    return render(request, 'sacola.html', context)


def api_condicoes_pagamento(request):
    metodo = request.GET.get('metodo')
    condicoes = CondicaoPagamento.objects.filter(ativo=True)
    
    if metodo:
        condicoes = condicoes.filter(tipo_pagamento=metodo)
    
    data = [{
        'id': c.id,
        'nome': c.nome,
        'tipo_display': c.get_tipo_pagamento_display(),
        'parcelas': c.parcelas,
        'juros': float(c.juros),
        'desconto': float(c.desconto)
    } for c in condicoes]
    
    return JsonResponse(data, safe=False)


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
        condicao_pagamento_id = request.POST.get('condicao_pagamento_id')

        errors = []
        condicoes_pagamento = CondicaoPagamento.objects.filter(ativo=True)
        viewCarrinho = getViewCarrinho(user_id, request)
        valor_geral = View_Carrinho.objects.filter(user_id=user_id).aggregate(Sum('valor_total')).get('valor_total__sum', 0.00)

        # Validações
        if not condicao_pagamento_id:
            errors.append("Selecione uma condição de pagamento!")
            context = {
                'errors': errors,
                'viewCarrinho': viewCarrinho,
                'condicoes_pagamento': condicoes_pagamento,
                'valor_geral': valor_geral,
                'clientes': Cliente.objects.all()
            }
            return render(request, 'sacola.html', context)

        if not cliente_id:
            errors.append("Selecione um cliente válido.")
            context = {
                'errors': errors,
                'viewCarrinho': viewCarrinho,
                'condicoes_pagamento': condicoes_pagamento,
                'valor_geral': valor_geral,
                'clientes': Cliente.objects.all()
            }
            return render(request, 'sacola.html', context)
        
        try:
            cliente = Cliente.objects.get(id=int(cliente_id))
            condicao_pagamento = CondicaoPagamento.objects.get(id=int(condicao_pagamento_id))
        except (ValueError, Cliente.DoesNotExist, CondicaoPagamento.DoesNotExist):
            errors.append("Cliente ou condição de pagamento não encontrados.")
            context = {
                'errors': errors,
                'viewCarrinho': viewCarrinho,
                'condicoes_pagamento': condicoes_pagamento,
                'valor_geral': valor_geral,
                'clientes': Cliente.objects.all()
            }
            return render(request, 'sacola.html', context)

        if not viewCarrinho:
            errors.append("Carrinho vazio. Adicione itens ao carrinho antes de realizar um pedido.")
            context = {
                'errors': errors,
                'condicoes_pagamento': condicoes_pagamento,
                'clientes': Cliente.objects.all()
            }
            return render(request, 'sacola.html', context)

        desconto = (valor_geral * condicao_pagamento.desconto / 100)
        valor_com_desconto = valor_geral - desconto
        juros = (valor_com_desconto * condicao_pagamento.juros / 100)
        valor_final = valor_com_desconto + juros
        valor_parcela = valor_final / condicao_pagamento.parcelas if condicao_pagamento.parcelas > 0 else valor_final

        try:
            with transaction.atomic():
                max_nr_pedido = Pedido.objects.filter(user_id=user_id).aggregate(Max('nr_pedido'))
                ultimo_nr_pedido = max_nr_pedido['nr_pedido__max'] or 0

                for car in viewCarrinho:
                    produto = Produto.objects.get(id=car['produto_id'])
                    if produto.estoque < car['quantidade']:
                        errors.append(f"Estoque insuficiente para o produto {produto.nome}")
                        context = {
                            'errors': errors,
                            'viewCarrinho': viewCarrinho,
                            'condicoes_pagamento': condicoes_pagamento,
                            'valor_geral': valor_geral,
                            'clientes': Cliente.objects.all()
                        }
                        return render(request, 'sacola.html', context)

                    pedido = Pedido(
                        nr_pedido=ultimo_nr_pedido + 1,
                        user_id=user_id,
                        cliente=cliente,
                        produto_id=car['produto_id'],
                        quantidade=car['quantidade'],
                        valor_unitario=car['valor_unitario'],
                        valor_total=valor_final,
                        data_pedido=timezone.now(),
                        metodo_pagamento=condicao_pagamento.tipo_pagamento,
                        parcelas=condicao_pagamento.parcelas,
                        condicao_pagamento=condicao_pagamento
                    )
                    pedido.save()
                    produto.estoque -= car['quantidade']
                    produto.save()

                # Cria contas a receber
                for i in range(condicao_pagamento.parcelas):
                    data_vencimento = timezone.now().date() + timedelta(days=condicao_pagamento.intervalo_parcelas * (i + 1))
                    
                    ContaReceber.objects.create(
                        pedido=pedido,
                        descricao=f"Venda Pedido {ultimo_nr_pedido + 1} - Parcela {i + 1}/{condicao_pagamento.parcelas}",
                        valor=valor_parcela,
                        data_vencimento=data_vencimento,
                        metodo_pagamento=condicao_pagamento.tipo_pagamento,
                        criado_em=timezone.now(),
                        recebido=False,
                        numero_parcela=i + 1
                    )

                limparItensCarrinho(request, user_id)
                return redirect('catalogo')

        except Exception as e:
            errors.append(f"Erro ao processar pedido: {str(e)}")
            context = {
                'errors': errors,
                'viewCarrinho': viewCarrinho,
                'condicoes_pagamento': condicoes_pagamento,
                'valor_geral': valor_geral,
                'clientes': Cliente.objects.all()
            }
            return render(request, 'sacola.html', context)

    else:
        viewCarrinho = getViewCarrinho(request.user.id, request)
        valor_geral = View_Carrinho.objects.filter(user_id=request.user.id).aggregate(Sum('valor_total')).get('valor_total__sum', 0.00)
        condicoes_ativas = CondicaoPagamento.objects.filter(ativo=True)
        metodos_disponiveis = CondicaoPagamento.TIPO_PAGAMENTO_CHOICES
        
        context = {
            'viewCarrinho': viewCarrinho,
            'valor_geral': valor_geral,
            'condicoes_pagamento': condicoes_ativas,
            'tipos_pagamento': dict(metodos_disponiveis),
            'clientes': Cliente.objects.all()
        }
        return render(request, 'sacola.html', context)


@login_required(login_url="/login/")
def meuspedidos(request):
    user_id = request.user.id
    viewPedidos = getViewPedidos(user_id, request)
    valor_geral = View_Pedido.objects.filter(user_id=user_id).aggregate(Sum('valor_total')).get('valor_total__sum', 0.00)
    clientes = Cliente.objects.all()

    cliente_filtro = request.GET.get('cliente')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    ordem = request.GET.get('ordem', 'antiga')
    numero_pedido = request.GET.get('numero_pedido')
    condicao_pagamento_filtro = request.GET.get('condicao_pagamento')

    pedidos = View_Pedido.objects.filter(user_id=user_id)

    if cliente_filtro:
        pedidos = pedidos.filter(cliente_nome__iexact=cliente_filtro) 
    
    if data_inicio:
        if data_fim: 
            pedidos = pedidos.filter(data_pedido__range=[data_inicio, data_fim])
        else: 
            pedidos = pedidos.filter(data_pedido__gte=data_inicio, data_pedido__lte=timezone.now())

    if ordem == 'recente':
        pedidos = pedidos.order_by('-nr_pedido')  
    elif ordem == 'antiga':
        pedidos = pedidos.order_by('nr_pedido') 

    if numero_pedido:
        pedidos = pedidos.filter(nr_pedido__iexact=numero_pedido)

    if condicao_pagamento_filtro:
        pedidos = pedidos.filter(condicao_pagamento_nome__iexact=condicao_pagamento_filtro)


    pedidos_dict = {}
    
    if pedidos.exists():
        for pedido in pedidos:
            nr_pedido = pedido.nr_pedido
            
            if nr_pedido not in pedidos_dict:
                valor_total = View_Pedido.objects.filter(nr_pedido=nr_pedido).aggregate(Sum('valor_total')).get('valor_total__sum', 0.00)
                parcelas = pedido.parcelas
                valor_parcela = valor_total / parcelas if parcelas > 0 else valor_total

                pedidos_dict[nr_pedido] = {
                    'data_pedido': pedido.data_pedido,
                    'itens': [],
                    'cliente_nome': pedido.cliente_nome,
                    'metodo_pagamento': pedido.metodo_pagamento,
                    'condicao_pagamento': pedido.condicao_pagamento_nome,
                    'parcelas': parcelas,
                    'id': pedido.id,
                    'valor_total': valor_total,
                    'valor_parcela': valor_parcela,
                    'parcelas_detalhadas': [],
                }
            
            pedidos_dict[nr_pedido]['itens'].append({
                'nome': pedido.nome,
                'quantidade': pedido.quantidade,
                'valor_unitario': pedido.valor_unitario,
                'valor_total': pedido.valor_total
            })
          
            if len(pedidos_dict[nr_pedido]['parcelas_detalhadas']) == 0 and pedido.parcelas > 0:
                vencimento_inicial = pedido.data_pedido
                for i in range(pedido.parcelas):
                    data_vencimento = vencimento_inicial + timedelta(days=30 * (i + 1))
                    pedidos_dict[nr_pedido]['parcelas_detalhadas'].append({
                        'numero_parcela': i + 1,
                        'valor_parcela': valor_parcela,
                        'data_vencimento': data_vencimento.strftime('%Y-%m-%d')
                    })

    condicoes_pagamento = View_Pedido.objects.filter(user_id=user_id)\
                            .values_list('condicao_pagamento_nome', flat=True)\
                            .distinct()

    context = {
        'viewPedidos': viewPedidos,
        'valor_geral': valor_geral,
        'pedidos_dict': pedidos_dict,
        'cliente_filtro': cliente_filtro,
        'clientes': clientes,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'ordem': ordem,
        'condicoes_pagamento': condicoes_pagamento,
        'condicao_pagamento_filtro': condicao_pagamento_filtro,  
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
    
    metodo_pagamento = pedido.metodo_pagamento
    parcelas = pedido.parcelas
    valor_parcela = total_geral / parcelas

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
        'metodo_pagamento': metodo_pagamento,  
        'parcelas': parcelas,                   
        'valor_parcela': valor_parcela, 
    }
    html = template.render(context)
    
    result = BytesIO()
    pdf = pisa.CreatePDF(html, dest=result)
    
    if pdf.err:
        return HttpResponse('Erro ao gerar PDF', status=500)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=pedido_{ped_id}.pdf'
    return response