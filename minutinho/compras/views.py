from django.shortcuts import render, redirect, get_object_or_404
from fornecedor.models import Fornecedor
from estoque.models import Produto
from financeiro.models import ContaPagar
from .forms import PedidoCompraForm, PedidoProdutoForm
from django.http import JsonResponse
from .models import PedidoCompra, PedidoProduto, ParcelaPedido
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from .functions import deletarCompra
import json
from django.http import HttpResponseBadRequest
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from datetime import timedelta, datetime
from django.db import transaction


# ESTUDAR JSON, SELECT2 E JAVASCRIPT USADO NESSA PARTE DE COMPRA!!

def compra(request):
    itens = PedidoCompra.objects.all()
    context = {
        'itens':itens,
    }
    return render(request, 'compra.html', context)

# View para autocomplete de fornecedores e produto
def fornecedor_autocomplete(request):
    term = request.GET.get('term', '') # Pega o termo da busca que digitei
    fornecedores = Fornecedor.objects.filter(nome__icontains=term) # faz o filtro doq eu pesquisei
    results = [{'id': f.id, 'text': f.nome} for f in fornecedores]  # 'text' é o que Select2 usa para exibir
    context ={
        'results': results,
    }
    return JsonResponse(context)

def produto_autocomplete(request):
    term = request.GET.get('term', '')
    produtos = Produto.objects.filter(nome__icontains=term) # mesma coisa que o de cima mas com produto
    results = [{'id': p.id, 'text': p.nome} for p in produtos]  
    context = {
        'results': results
    }
    return JsonResponse(context)

def criar_pedido(request):
    if request.method == 'POST':
        pedido_form = PedidoCompraForm(request.POST)
        errors = []

        fornecedor_id = request.POST.get('fornecedor')
        if not fornecedor_id:
            errors.append("O campo 'Fornecedor' é obrigatório.")

        try:
            produtos = json.loads(request.POST.get('produtos', '[]'))
            quantidades = json.loads(request.POST.get('quantidades', '[]'))
            precos_unitarios = json.loads(request.POST.get('precos_unitarios', '[]'))
            metodo_pagamento = request.POST.get('metodo_pagamento')
            parcelamento = int(request.POST.get('parcelamento', '1')) if metodo_pagamento == 'cartao_credito' else 1

            if len(produtos) == 0:
                errors.append("Pelo menos um produto deve ser adicionado.")

            for quantidade in quantidades:
                if Decimal(quantidade) < 0:
                    errors.append("A quantidade não pode ser negativa.")

            for preco_unitario in precos_unitarios:
                if Decimal(preco_unitario) < 0:
                    errors.append("O preço unitário não pode ser negativo.")

        except json.JSONDecodeError as e:
            errors.append("Erro ao decodificar JSON dos produtos.")
        except ValueError as e:
            errors.append("Valores inválidos para quantidade ou preço unitário.")

        if errors:
            context = {
                'pedido_form': pedido_form,
                'errors': errors
            }
            return render(request, 'criar_pedido.html', context)

        if pedido_form.is_valid():
            pedido = pedido_form.save(commit=False)  # o commit false faz com que o formulario não seja salvo ainda
            total_pedido = Decimal(0)

            pedido.save()

            try:
                if len(produtos) == len(quantidades) == len(precos_unitarios):
                    for produto_id, quantidade, preco_unitario in zip(produtos, quantidades, precos_unitarios):
                        if produto_id and quantidade and preco_unitario:
                            try:
                                quantidade = Decimal(quantidade.replace(',', '.'))
                                preco_unitario = Decimal(preco_unitario.replace(',', '.'))
                                produto = get_object_or_404(Produto, id=int(produto_id))

                                produto.estoque += quantidade
                                produto.save()

                                total_pedido += quantidade * preco_unitario

                                PedidoProduto.objects.create(
                                    pedido=pedido,  
                                    produto=produto,
                                    quantidade=quantidade,
                                    preco_unitario=preco_unitario
                                )
                            except (ValueError, InvalidOperation) as e:
                                errors.append(f"Erro ao processar o produto {produto_id}: {e}")
                            except Exception as e:
                                errors.append(f"Erro ao salvar o produto {produto_id}: {e}")
                else:
                    errors.append("A quantidade de produtos, quantidades e preços unitários não corresponde.")
            except Exception as e:
                errors.append(f"Erro ao processar os produtos: {e}")

            if errors:
                context = {
                    'pedido_form': pedido_form,
                    'errors': errors
                }
                return render(request, 'criar_pedido.html', context)

            # Atualiza o valor da compra
            pedido.total = total_pedido
            pedido.save()  

            if metodo_pagamento in ['cartao_credito', 'boleto', 'pix', 'cartao_debito']:
                data_base = pedido.data_pedido or timezone.now().date()

                if metodo_pagamento == 'cartao_credito':
                    pedido.parcelas = parcelamento
                    pedido.salvar_parcelas()

                    valor_parcela = total_pedido / parcelamento

                    for i in range(parcelamento):
                        data_vencimento = data_base + timedelta(days=(i + 1) * 30)
                        ContaPagar.objects.create(
                            descricao=f"Parcela {i + 1} do Pedido {pedido.id}",
                            valor=valor_parcela,
                            data_vencimento=data_vencimento,
                            metodo_pagamento=metodo_pagamento,
                            numero_parcela=i + 1,
                            pago=False,
                            pedido=pedido,
                            editavel=False,
                        )
                else:
                    data_vencimento = data_base + timedelta(days=7) 
                    ContaPagar.objects.create(
                        descricao=f"Pagamento à vista do Pedido {pedido.id}",
                        valor=total_pedido,
                        data_vencimento=data_vencimento,
                        metodo_pagamento=metodo_pagamento,
                        numero_parcela=1, 
                        pago=False,
                        pedido=pedido,
                        editavel=False,
                    )

            return redirect('compra')
    else:
        pedido_form = PedidoCompraForm()

    return render(request, 'criar_pedido.html', {'pedido_form': pedido_form})


def removercompra(request, item_id):
    try:
        deletarCompra(item_id) # função no function para deletar do banco de dados
    except Exception as e:
        print(f"Erro ao remover item: {e}")
    return redirect('compra')

def editar_pedido(request, item_id):
    pedido = get_object_or_404(PedidoCompra, id=item_id)
    errors = []

    if request.method == 'POST':
        data_pedido = request.POST.get('data_pedido')
        fornecedor_id = request.POST.get('fornecedor')
        produtos = request.POST.get('produtos', '').split(',')
        quantidades = request.POST.get('quantidades', '').split(',')
        precos_unitarios = request.POST.get('precos_unitarios', '').split(',')
        parcelamento = int(request.POST.get('parcelamento', '1'))
        metodo_pagamento = request.POST.get('metodo_pagamento')

        if not data_pedido:
            errors.append("A data do pedido é obrigatória.")
        if not fornecedor_id:
            errors.append("O fornecedor é obrigatório.")
        if len(produtos) == 0 or len(quantidades) == 0 or len(precos_unitarios) == 0:
            errors.append("Pelo menos um produto deve ser adicionado ao pedido.")

        if errors:
            context = {
                'pedido': pedido,
                'errors': errors
            }
            return render(request, 'editar_pedido.html', context)

        # Atualizar dados básicos do pedido
        pedido.fornecedor_id = fornecedor_id
        pedido.data_pedido = data_pedido
        pedido.metodo_pagamento = metodo_pagamento
        pedido.save()

        if len(produtos) == len(quantidades) == len(precos_unitarios):
            # Restaurar o estoque dos produtos antigos antes de excluir
            produtos_antigos = PedidoProduto.objects.filter(pedido=pedido)
            for item in produtos_antigos:
                item.produto.estoque -= item.quantidade
                item.produto.save()

            PedidoProduto.objects.filter(pedido=pedido).delete()

            for prod_id, quantidade, preco_unitario in zip(produtos, quantidades, precos_unitarios):
                try:
                    if not prod_id:
                        continue  # Ignorar se não tiver nd

                    produto = Produto.objects.get(id=int(prod_id))
                    quantidade = Decimal(quantidade.replace(',', '.'))
                    preco_unitario = Decimal(preco_unitario.replace(',', '.'))

                    if quantidade <= 0:
                        errors.append(f"A quantidade para o produto '{produto.nome}' deve ser maior que zero.")
                    if preco_unitario < 0:
                        errors.append(f"O preço unitário para o produto '{produto.nome}' não pode ser negativo.")

                    if quantidade > 0 and preco_unitario >= 0:
                        produto.estoque += quantidade
                        produto.save()

                        PedidoProduto.objects.create(
                            pedido=pedido,
                            produto=produto,
                            quantidade=quantidade,
                            preco_unitario=preco_unitario
                        )
                except Produto.DoesNotExist:
                    errors.append(f"Produto com ID {prod_id} não encontrado.")
                except (ValueError, InvalidOperation):
                    errors.append("Valores inválidos para quantidade ou preço.")
        else:
            errors.append("Número de produtos, quantidades e preços não correspondem.")

        if errors:
            context = {
                'pedido': pedido,
                'errors': errors
            }
            return render(request, 'editar_pedido.html', context)

        pedido.total = pedido.calcular_total()
        pedido.save()

        if metodo_pagamento == 'cartao_credito':
            valor_total = pedido.calcular_total()

            if valor_total is None or valor_total <= 0:
                errors.append("O valor total do pedido é inválido.")
            else:
                with transaction.atomic():
                    pedido.parcelas_pedido.all().delete() 
                    ContaPagar.objects.filter(pedido=pedido).delete()  

                    valor_parcela = (valor_total / parcelamento).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    data_base = pedido.data_pedido or timezone.now().date()

                    # Se data_base for uma string, converta-a para date
                    if isinstance(data_base, str):
                        try:
                            data_base = datetime.strptime(data_base, '%Y-%m-%d').date()
                        except ValueError:
                            errors.append("Formato de data inválido. Use o formato YYYY-MM-DD.")
                            context = {
                                'pedido': pedido,
                                'errors': errors
                            }
                            return render(request, 'editar_pedido.html', context)

                    for i in range(parcelamento):
                        data_vencimento = data_base + timedelta(days=(i + 1) * 30)

                        parcela = ParcelaPedido.objects.create(
                            pedido=pedido,
                            numero_parcela=i + 1,
                            valor_parcela=valor_parcela,
                            data_vencimento=data_vencimento
                        )

                        ContaPagar.objects.create(
                            descricao=f"Parcela {i + 1} do Pedido {pedido.id}",
                            valor=valor_parcela,
                            data_vencimento=data_vencimento,
                            metodo_pagamento=metodo_pagamento,
                            numero_parcela=i + 1,
                            pago=False,
                            pedido=pedido,
                            editavel=False,
                        )

        return redirect('compra')

    produtos_pedido = pedido.pedidoproduto_set.all()
    context = {
        'pedido': pedido,
        'produtos_pedido': produtos_pedido,
        'errors': errors
    }
    return render(request, 'editar_pedido.html', context)

def editar(request, item_id):
    pedido = get_object_or_404(PedidoCompra, id=item_id)
    form = PedidoCompraForm(instance=pedido)
    context = {
        'pedido': pedido,
        'form': form
    }
    return render(request, 'editar_pedido.html', context)

def notacompra(request, item_id):
    compra = get_object_or_404(PedidoCompra, id=item_id)
    fornecedor = compra.fornecedor  
    itens = PedidoProduto.objects.filter(pedido=compra)

    tipo_pessoa = fornecedor.tipo_pessoa.strip() if fornecedor.tipo_pessoa else None

    if tipo_pessoa == 'Pessoa Física' and fornecedor.cpf:
        documento = fornecedor.cpf
    elif tipo_pessoa == 'Pessoa Jurídica' and fornecedor.cnpj:
        documento = fornecedor.cnpj
    else:
        documento = 'Documento não informado'


    # Criação da lista de itens e cálculo do total de produtos
    quantidade_total = 0
    itens_detalhados = []
    for item in itens:
        produto = item.produto
        itens_detalhados.append({
            'produto_id': produto.id,
            'nome': produto.nome,
            'quantidade': item.quantidade,
            'valor_unitario': item.preco_unitario,
            'valor_total': item.preco_unitario * item.quantidade,
        })
        quantidade_total += item.quantidade

    total_geral = sum(item['valor_total'] for item in itens_detalhados)

    # Carrega o template HTML para o PDF
    template = get_template('pdfcompra.html')
    context = {
        'pedido': compra,
        'itens': itens_detalhados,
        'total_geral': total_geral,
        'quantidade_total': quantidade_total,
        'fornecedor_nome': fornecedor.nome,
        'fornecedor_cidade': fornecedor.cidade,
        'fornecedor_estado': fornecedor.estado,
        'fornecedor_tipo_pessoa': fornecedor.tipo_pessoa,
        'documento': documento,
        'fornecedor_endereco':fornecedor.endereco,
        'fornecedor_numero':fornecedor.numero,  
    }
    html = template.render(context)

    # Cria um buffer para armazenar o PDF gerado
    result = BytesIO()
    pdf = pisa.CreatePDF(html, dest=result)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=compra_{item_id}.pdf'
    return response