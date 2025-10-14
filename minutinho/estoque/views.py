from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Categoria
from django.contrib.auth.decorators import login_required
from estoque.functions import deletarProduto, removerCategoria
from cliente.models import Cliente
from venda.models import View_Pedido, Pedido
from financeiro.models import ContaPagar, ContaReceber, Extrato
from django.db.models import Sum, Count, F, Value, DecimalField
from django.utils import timezone
import json
from django.db.models.functions import Coalesce



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
    hoje = timezone.now().date()
    atual = hoje.replace(day=1)

    entradas_pagas = (
        Extrato.objects.filter(tipo='entrada', status='pago')
        .aggregate(total=Coalesce(Sum('valor'), Value(Decimal('0.00')), output_field=DecimalField()))['total']
    )

    saidas_pagas = (
        Extrato.objects.filter(tipo='saida', status='pago')
        .aggregate(total=Coalesce(Sum('valor'), Value(Decimal('0.00')), output_field=DecimalField()))['total']
    )

    saldo_extrato = entradas_pagas - saidas_pagas

    receber = ContaReceber.objects.filter(recebido=False).aggregate(total=Sum('valor'))['total'] or 0
    pagar = ContaPagar.objects.filter(pago=False).aggregate(total=Sum('valor'))['total'] or 0
    clienteMes = Cliente.objects.filter(data_cadastro__gte=atual).count()

    contasPagarVencidas = ContaPagar.objects.filter(pago=False, data_vencimento__lt=hoje).count()
    contasReceberVencidas = ContaReceber.objects.filter(recebido=False, data_vencimento__lt=hoje).count()
    contasVencidas = contasPagarVencidas + contasReceberVencidas
    
    estoqueBaixo = Produto.objects.filter(estoque__lte=F('estoque')).order_by('estoque')[:5]
    
    vendas = Pedido.objects.order_by('-data_pedido', '-id')[:5]

    labels_faturamento = []
    data_faturamento = []
    for i in range(6):
        mes = hoje.month - i
        ano = hoje.year
        if mes <= 0:
            mes += 12
            ano -= 1
        
        mes_nome = timezone.datetime(ano, mes, 1).strftime('%b')
        labels_faturamento.insert(0, f"{mes_nome}/{ano}")

        faturamento = Pedido.objects.filter(data_pedido__year=ano, data_pedido__month=mes).aggregate(total=Sum('valor_total'))['total'] or 0
        data_faturamento.insert(0, float(faturamento))

    top_produtos_query = Pedido.objects.filter(data_pedido__gte=atual, produto__isnull=False).values('produto__nome').annotate(total_vendido=Count('produto')).order_by('-total_vendido')[:5]
    labels_top_produtos = [item['produto__nome'] for item in top_produtos_query]
    data_top_produtos = [item['total_vendido'] for item in top_produtos_query]

    context = {
        'saldo_extrato': saldo_extrato,
        'receber': receber,
        'pagar': pagar,
        'clienteMes': clienteMes,
        'contasVencidas': contasVencidas,
        'estoqueBaixo': estoqueBaixo,
        'vendas': vendas,
        'labels_faturamento': json.dumps(labels_faturamento),
        'data_faturamento': json.dumps(data_faturamento),
        'labels_top_produtos': json.dumps(labels_top_produtos),
        'data_top_produtos': json.dumps(data_top_produtos),
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
