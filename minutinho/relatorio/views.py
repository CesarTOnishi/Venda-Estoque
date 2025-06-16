from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from venda.models import View_Pedido
from datetime import datetime, timedelta
from estoque.models import Produto


from django.shortcuts import render, redirect, get_object_or_404

def relatorio(request):
    return render(request, 'relatorio.html')

def relatoriovenda(request):
    filtro = request.GET.get('filtro', 'quantidade_alta')

    queryset = View_Pedido.objects.values('produto_id', 'nome',).annotate(
        quantidade_total=Sum('quantidade'),
        valor_total=Sum('valor_total')
    )

    # Filtros e ordenação
    if filtro == 'quantidade_alta':
        maisvendido = queryset.order_by('-quantidade_total')[:10]
    elif filtro == 'quantidade_baixa':
        maisvendido = queryset.order_by('quantidade_total')[:10]
    elif filtro == 'valor_alto':
        maisvendido = queryset.order_by('-valor_total')[:10]
    elif filtro == 'valor_baixo':
        maisvendido = queryset.order_by('valor_total')[:10]
    else:
        maisvendido = queryset 

    context = {
        'maisvendido': maisvendido
    }

    template_path = 'maisvendido.html'
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_mais_vendidos.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Erro ao gerar o PDF', status=500)

    return response

def relatorioestoque(request):
    filtro = request.GET.get('filtro', 'estoque_total')

    queryset = Produto.objects.values('id', 'nome', 'estoque', 'categoria_nome').annotate(
        quantidade_total=Sum('estoque'),
    )

    # Filtros e ordenação
    if filtro == 'sem_estoque':
        estoque = queryset.filter(quantidade_total__lte=0)
    elif filtro == 'pouco_estoque':
        estoque = queryset.filter(quantidade_total__gt=0, quantidade_total__lte=10)
    elif filtro == 'estoque_alto':
        estoque = queryset.filter(quantidade_total__gt=10)
    else:  # estoque_total
        estoque = queryset.order_by('-quantidade_total')

    for produto in estoque:
        if produto['quantidade_total'] <= 0:
            produto['status'] = 'fora_de_estoque'  
        elif 1 <= produto['quantidade_total'] <= 10:
            produto['status'] = 'pouco_estoque' 
        else:
            produto['status'] = 'muito_estoque'  

    context = {
        'estoque':estoque,
    }

    template_path = 'estoqueatual.html'
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_mais_vendidos.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Erro ao gerar o PDF', status=500)

    return response