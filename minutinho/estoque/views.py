from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Categoria
from django.contrib.auth.decorators import login_required
from estoque.functions import deletarProduto, removerCategoria
from cliente.models import Cliente
from venda.models import View_Pedido
from django.db.models import Sum

@login_required(login_url="/login/")
def estoque(request):
    categorias = Categoria.objects.all()
    if request.method == "GET":
        context= {
            'categorias':categorias,
        }
        return render(request, 'addprodutos.html', context)
    else:
        nome = request.POST.get('nome')
        estoque = request.POST.get('estoque')
        descricao = request.POST.get('descricao')
        preco = request.POST.get('preco')
        categoria_id = request.POST.get('categoria')

        produtos = Produto.objects.all()
        errors = []

        if not nome or not descricao or not preco or not categoria:
            errors.append("Todos os campos são obrigatórios.")

        if estoque.strip():
            try:
                estoque_int = int(estoque)
                if estoque_int < 0:
                    errors.append('O estoque não pode ser negativo')
            except ValueError:
                errors.append("Estoque deve ser um número inteiro válido.")
        else:
            estoque_int = None

        if preco.strip():
            try:
                preco_dec = Decimal(preco.replace(",", "."))
                if preco_dec < 0:
                    errors.append('O preço não pode ser negativo')
            except InvalidOperation:
                errors.append("Preço inválido.")
        else:
            preco_dec = None

        
        categoria_obj = Categoria.objects.filter(id=categoria_id).first()
        if not categoria_obj:
            errors.append('Categoria inválida.')

        if errors:
            context = {
                'errors': errors,
                'nome': nome,
                'estoque': estoque,
                'descricao': descricao,
                'preco': preco,
                'produtos': produtos,
                'categorias': categorias,
            }
            return render(request, 'addprodutos.html', context)

        produto = Produto(nome=nome, estoque=estoque_int, descricao=descricao, preco=preco_dec, categoria_nome=categoria)
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

@login_required(login_url="/login/")
def lista(request):
    categorias = Categoria.objects.all()
    produtos = Produto.objects.all().order_by('nome')

    filtroCategoria = request.GET.get('categoria')
    if filtroCategoria:
        categoria_obj = Categoria.objects.filter(id=filtroCategoria).first()
        if categoria_obj:
            produtos = produtos.filter(categoria_nome=categoria_obj.nome).order_by("nome")

    search_query = request.GET.get('search')
    if search_query:
        produtos = produtos.filter(nome__icontains=search_query)

    context = {
        'produtos': produtos,
        'categorias': categorias,
        'filtroCategoria' : filtroCategoria,
    }
    return render(request, 'lista.html', context)

@login_required(login_url="/login/")
def editarProd(request, prod_id):
    categorias = Categoria.objects.all()
    produto = Produto.objects.get(id=prod_id)
    context = {
        'produto': produto,
        'categorias':categorias,
    }
    return render(request, "editar.html", context)

@login_required(login_url="/login/")
def removerProd(request, prod_id):
    deletarProduto(prod_id)
    return redirect('lista')

@login_required(login_url="/login/")
def salvar(request, prod_id):
    produto = Produto.objects.get(id=prod_id)
    nome = request.POST.get('nome')
    estoque = request.POST.get('estoque')
    descricao = request.POST.get('descricao')
    preco = request.POST.get('preco')
    categoria_id = request.POST.get('categoria')

    errors = []

    try:
        preco_dec = Decimal(preco.replace(",", "."))
        estoque_int = int(estoque.strip()) if estoque.strip() else 0  
    except InvalidOperation:
        errors.append("Preço inválido ou estoque inválido.")

    if not nome:
        errors.append("O nome do produto é obrigatório")
    
    if not preco:
        errors.append("O Preco é obrigtório!")

    if preco_dec < 0:
        errors.append('O preço não pode ser negativo.')
    if estoque_int < 0:
        errors.append('O estoque não pode ser negativo.')

    
    categoria_obj = Categoria.objects.filter(id=categoria_id).first()
    if not categoria_obj:
        errors.append('Categoria inválida.')

    if errors:
        context = {
            'errors': errors,
            'produto': produto,
            'produtos': Produto.objects.all().order_by('nome'),
            'categorias': Categoria.objects.all(),
            'nome' : nome,
            'estoque' : estoque,
            'descricao' : descricao,
            'preco' : preco,
        }
        return render(request, "editar.html", context)

    produto.preco = preco_dec
    produto.nome = nome
    produto.estoque = estoque_int
    produto.descricao = descricao
    produto.categoria = categoria_obj
    produto.save()
    return redirect('lista')

@login_required(login_url="/login/")
def categoria(request):
    categorias = Categoria.objects.all()
    context = {
        'categorias' : categorias,
    }
    return render(request, 'categoria.html', context)

@login_required(login_url="/login/")
def cadastroCategoria(request):
    return render(request, 'cadastrocategoria.html')

@login_required(login_url="/login/")
def cadcat(request):
    if request.method == "POST":
        errors = []
        categoria_nome = request.POST.get('categoria')

        if not categoria_nome:
            errors.append('O nome da categoria é obrigatório.')

        elif Categoria.objects.filter(nome=categoria_nome).exists(): 
            errors.append('Essa categoria já existe.')

        if errors:
            context = {
                'errors': errors
                }
            return render(request, 'cadastrocategoria.html', context)

        nova_categoria = Categoria(nome=categoria_nome)
        nova_categoria.save()
        return redirect('categoria')
    
    return render(request, 'cadastrocategoria.html')

@login_required(login_url="/login/")
def editCategoria(request, cat_id):
    categoria = Categoria.objects.get(id=cat_id)
    context = {
        'categoria': categoria
    }
    return render(request, "editarcategoria.html", context)

@login_required(login_url="/login/")
def editarCategoria(request, cat_id):
    categoria = get_object_or_404(Categoria, id=cat_id)

    if request.method == 'POST':
        nome_categoria = request.POST.get('categoria')
        errors = []

        if not nome_categoria:
            errors.append('O nome da categoria é obrigatório.')

        if Categoria.objects.filter(nome=nome_categoria).exclude(id=cat_id).exists():
            errors.append('Essa categoria já existe.')

        if errors:
            context = {
                'categoria': categoria,
                'errors': errors
            }
            return render(request, 'categoria.html', context)

        categoria.nome = nome_categoria
        categoria.save()

    context = {
        'categoria': categoria,
    }
    return redirect('categoria')
    
@login_required(login_url="/login/")
def deletarCategoria(request, cat_id):
    removerCategoria(cat_id)
    return redirect('categoria')
