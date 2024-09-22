from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from .models import Produto
from django.contrib.auth.decorators import login_required
from estoque.functions import deletarProduto
from cliente.models import Cliente
from venda.models import View_Pedido
from django.db.models import Sum

@login_required(login_url="/login/")
def estoque(request):
    if request.method == "GET":
        return render(request, 'addprodutos.html')
    else:
        nome = request.POST.get('nome')
        estoque = request.POST.get('estoque')
        descricao = request.POST.get('descricao')
        preco = request.POST.get('preco')

        produtos = Produto.objects.all()
        errors = []

        # Validação dos campos obrigatórios
        if not nome or not descricao or not preco:
            errors.append("Todos os campos são obrigatórios.")

        # Validação do estoque
        if estoque.strip():
            try:
                estoque_int = int(estoque)
                if estoque_int < 0:
                    errors.append('O estoque não pode ser negativo')
            except ValueError:
                errors.append("Estoque deve ser um número inteiro válido.")
        else:
            estoque_int = None

        # Validação do preço
        if preco.strip():
            try:
                preco_dec = Decimal(preco.replace(",", "."))
                if preco_dec < 0:
                    errors.append('O preço não pode ser negativo')
            except InvalidOperation:
                errors.append("Preço inválido.")
        else:
            preco_dec = None

        if errors:
            context = {
                'errors': errors,
                'nome': nome,
                'estoque': estoque,
                'descricao': descricao,
                'preco': preco,
                'produtos': produtos
            }
            return render(request, 'addprodutos.html', context)

        # Salvar o produto
        produto = Produto(nome=nome, estoque=estoque_int, descricao=descricao, preco=preco_dec)
        produto.save()
        return redirect('lista')

@login_required(login_url="/login/")
def tela(request):
    return render(request, 'tela.html')

@login_required(login_url="/login/")
def inicial(request):
    user_id = request.user.id
    quantidade_clientes = Cliente.objects.count()
    quantidade_pedidos = View_Pedido.objects.values('nr_pedido').distinct().count()
    total_vendas = View_Pedido.objects.aggregate(total_vendas=Sum('valor_total'))['total_vendas'] or 0
    pedidos_agregados = (View_Pedido.objects.values('nr_pedido', 'cliente_nome').annotate(
            quantidade_total=Sum('quantidade'),
            valor_total=Sum('valor_total')
        ).order_by('-nr_pedido')[:5]
    )

    context = {
        'quantidade_clientes': quantidade_clientes,
        'quantidade_pedidos': quantidade_pedidos,
        'total_vendas': total_vendas,
        'pedidos': pedidos_agregados,
    }
    return render(request, 'inicial.html', context)

def lista(request):
    produtos = Produto.objects.all().order_by('nome')
    context = {
        'produtos': produtos
    }
    return render(request, 'lista.html', context)

def editar(request, prod_id):
    produto = Produto.objects.get(id=prod_id)
    context = {
        'produto': produto
    }
    return render(request, "editar.html", context)

def remover(request, prod_id):
    deletarProduto(prod_id)
    return redirect('lista')

def salvar(request, prod_id):
    produto = Produto.objects.get(id=prod_id)
    nome = request.POST.get('nome')
    estoque = request.POST.get('estoque')
    descricao = request.POST.get('descricao')
    preco = request.POST.get('preco')

    errors = []

    try:
        preco_dec = Decimal(preco.replace(",", "."))
        estoque_int = int(estoque) if estoque.strip() else 0
    except InvalidOperation:
        errors.append("Preço inválido ou estoque inválido.")

    if float(preco) < 0:
        errors.append('O Preço não pode ser negativo')
    if int(estoque) < 0:
        errors.append('O estoque não pode ser negativo')

    if errors:
        context = {
            'errors': errors,
            'produto': produto,
            'produtos': Produto.objects.all().order_by('nome')
        }
        return render(request, "editar.html", context)

    produto.preco = preco_dec
    produto.nome = nome
    produto.estoque = estoque_int
    produto.descricao = descricao
    produto.save()
    return redirect('lista')
