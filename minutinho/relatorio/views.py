from django.db.models import Sum, Count
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from venda.models import View_Pedido
from datetime import datetime, timedelta
from estoque.models import Produto
from cliente.models import Cliente
from funcionario.models import Funcionarios
from venda.models import Pedido
from fornecedor.models import Fornecedor
from financeiro.models import ContaPagar, ContaReceber, Extrato
from django.utils.dateparse import parse_date


from django.shortcuts import render, redirect, get_object_or_404

def relatorio(request):
    return render(request, 'relatorio.html')


def relatorioestoque(request):
    filtro = request.GET.get('filtro', 'estoque_total')

    queryset = Produto.objects.values(
        'id', 'nome', 'estoque', 'categoria__nome'
    ).annotate(
        quantidade_total=Sum('estoque')
    )

    if filtro == 'sem_estoque':
        estoque = queryset.filter(quantidade_total__lte=0)
    elif filtro == 'pouco_estoque':
        estoque = queryset.filter(quantidade_total__gt=0, quantidade_total__lte=10)
    elif filtro == 'estoque_alto':
        estoque = queryset.filter(quantidade_total__gt=10)
    else: 
        estoque = queryset.order_by('-quantidade_total')

    for produto in estoque:
        if produto['quantidade_total'] <= 0:
            produto['status'] = 'fora_de_estoque'
        elif 1 <= produto['quantidade_total'] <= 10:
            produto['status'] = 'pouco_estoque'
        else:
            produto['status'] = 'muito_estoque'

    context = {'estoque': estoque}

    template_path = 'estoqueatual.html'
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=\"relatorio_estoque.pdf\"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Erro ao gerar o PDF', status=500)

    return response

def relatorioclientes(request):
    clientes = Cliente.objects.all()

    context = {
        "clientes": clientes,
    }

    template_path = "todosclientes.html"
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="relatorio_clientes.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Erro ao gerar o PDF", status=500)

    return response

def relatoriofuncionarios(request):
    funcionarios = Funcionarios.objects.all()

    context = {
        "funcionarios": funcionarios,
    }

    template_path = "todosfuncionarios.html" 
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="relatorio_funcionarios.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Erro ao gerar o PDF", status=500)

    return response

def relatoriovendapagamento(request):
    vendas_pagamento = (
        Pedido.objects.values("metodo_pagamento")
        .annotate(total_vendas=Sum("valor_total"), qtd=Count("id"))
        .order_by("metodo_pagamento")
    )

    context = {
        "vendas_pagamento": vendas_pagamento,
    }

    template_path = "vendapagamento.html"  # template HTML
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="relatorio_vendas_pagamento.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Erro ao gerar o PDF", status=500)

    return response

def relatoriofornecedores(request):
    fornecedor_nome = request.GET.get('fornecedor', 'todos')

    if fornecedor_nome.lower() == 'todos' or not fornecedor_nome:
        fornecedores = Fornecedor.objects.all()
    else:
        fornecedores = Fornecedor.objects.filter(nome__icontains=fornecedor_nome)

    context = {"fornecedores": fornecedores}

    template_path = "todosfornecedores.html"
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="relatorio_fornecedores.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Erro ao gerar o PDF", status=500)

    return response

def autocomplete_fornecedor(request):
    query = request.GET.get('q', '')
    fornecedores = Fornecedor.objects.filter(nome__icontains=query)[:10]
    results = [{"id": f.id, "nome": f.nome} for f in fornecedores]
    return JsonResponse(results, safe=False)

def relatoriocontas(request):
    tipo_conta = request.GET.get("tipo_conta", "todos")
    data_inicio = request.GET.get("inicio")
    data_fim = request.GET.get("fim")

    contas_pagar = ContaPagar.objects.all()
    contas_receber = ContaReceber.objects.all()

    if data_inicio and data_fim:
        try:
            inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
            contas_pagar = contas_pagar.filter(data_vencimento__range=(inicio, fim))
            contas_receber = contas_receber.filter(data_vencimento__range=(inicio, fim))
        except ValueError:
            pass

    if tipo_conta == "pagar":
        contas = list(contas_pagar)
    elif tipo_conta == "receber":
        contas = list(contas_receber)
    else:
        contas = list(contas_pagar) + list(contas_receber)

    context = {"contas": contas}

    template_path = "contas.html"
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="relatorio_contas.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Erro ao gerar o PDF", status=500)

    return response

def relatorioextrato(request):
    inicio = request.GET.get('inicio')
    fim = request.GET.get('fim')

    extrato = Extrato.objects.all().order_by('data_transacao')

    if inicio and fim:
        extrato = extrato.filter(
            data_transacao__date__gte=inicio,
            data_transacao__date__lte=fim
        )

    context = {
        'extrato': extrato,
    }

    template_path = "relatorioextrato.html"
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="extrato_financeiro.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Erro ao gerar o PDF", status=500)

    return response

def relatoriovendas(request):
    inicio = request.GET.get('inicio')
    fim = request.GET.get('fim')

    vendas = View_Pedido.objects.all().order_by('data_pedido')

    if inicio and fim:
        vendas = vendas.filter(
            data_pedido__gte=inicio,
            data_pedido__lte=fim
        )

    context = {
        'vendas': vendas,
        'inicio': inicio,
        'fim': fim
    }

    template_path = "maisvendido.html"
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="relatorio_vendas_periodo.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Erro ao gerar o PDF", status=500)

    return response