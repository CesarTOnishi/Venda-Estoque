from django.shortcuts import render, redirect, get_object_or_404
from fornecedor.models import Fornecedor
from estoque.models import Produto
from .forms import PedidoCompraForm, PedidoProdutoForm
from django.http import JsonResponse
from .models import PedidoCompra, PedidoProduto
from decimal import Decimal, InvalidOperation
from .functions import deletarCompra
import json
from django.http import HttpResponseBadRequest
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template


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
        errors = []  # armazena os erros

        # Verificação de campos obrigatórios
        fornecedor_id = request.POST.get('fornecedor')
        if not fornecedor_id:
            errors.append("O campo 'Fornecedor' é obrigatório.") # cadocaso não tenha fornecedor

        # Validação de produtos, quantidades e preços
        try:
            produtos = json.loads(request.POST.get('produtos', '[]'))
            quantidades = json.loads(request.POST.get('quantidades', '[]')) # Obtem os dados com json
            precos_unitarios = json.loads(request.POST.get('precos_unitarios', '[]'))# erro ao tentar no metodo normal de request.post,get

            if len(produtos) == 0:
                errors.append("Pelo menos um produto deve ser adicionado.")

            for quantidade in quantidades:
                if Decimal(quantidade) < 0:
                    errors.append("A quantidade não pode ser negativa.")   # validação

            for preco_unitario in precos_unitarios:
                if Decimal(preco_unitario) < 0:
                    errors.append("O preço unitário não pode ser negativo.")

        except json.JSONDecodeError as e:
            errors.append("Erro ao decodificar JSON dos produtos.") # caso de errado no json
        
        if errors:
            context = {
                'pedido_form': pedido_form,  # caso ocorra algum erro aparecer
                'errors': errors
            }
            return render(request, 'criar_pedido.html', context)

        if pedido_form.is_valid():
            pedido = pedido_form.save() # caso o formulario esteja certo ele vai salvar
            
            try:
                if len(produtos) == len(quantidades) == len(precos_unitarios): # verifica se os dados estão iguais
                    for produto_id, quantidade, preco_unitario in zip(produtos, quantidades, precos_unitarios):
                        if produto_id and quantidade and preco_unitario:
                            try:
                                # Substituir vírgulas por pontos
                                quantidade = quantidade.replace(',', '.')
                                preco_unitario = preco_unitario.replace(',', '.')

                                # Converter para Decimal
                                quantidade = Decimal(quantidade)
                                preco_unitario = Decimal(preco_unitario)

                                # Converter produto_id para inteiro e buscar o produto
                                produto_id = int(produto_id)
                                produto = get_object_or_404(Produto, id=produto_id)

                                produto.estoque += quantidade # função para adcionar ao estoque
                                produto.save() # salva

                                # Cria o relacionamento entre o pedido e o produto (tabela associativa)
                                PedidoProduto.objects.create(
                                    pedido=pedido,
                                    produto=produto,
                                    quantidade=quantidade,
                                    preco_unitario=preco_unitario
                                )
                            except (ValueError, InvalidOperation) as e:
                                print(f'Erro ao converter valores: {e}')
                                print(f'Valores recebidos - produto_id: {produto_id}, quantidade: {quantidade}, preco_unitario: {preco_unitario}')
                            except Exception as e:
                                print(f'Erro ao salvar produto: {e}')
                else:
                    errors.append("A quantidade de produtos, quantidades e preços unitários não corresponde.")

            except json.JSONDecodeError as e:
                errors.append("Erro ao decodificar JSON dos produtos.")

            if errors:
                context = {
                    'pedido_form': pedido_form,
                    'errors': errors
                }
                return render(request, 'criar_pedido.html', context)
            #TUDO EM RELAÇÃO A ERRO E VALIDAÇÃO

            pedido.calcular_total() # faz o calculo do valor total do pedido, codigo no models!!
            return redirect('compra')

    else:
        pedido_form = PedidoCompraForm() # exibe o formulario vazio para criar um novo pedido
    
    return render(request, 'criar_pedido.html', {'pedido_form': pedido_form})

def removercompra(request, item_id):
    try:
        deletarCompra(item_id) # função no function para deletar do banco de dados
    except Exception as e:
        # Lidar com a exceção, como registrar o erro ou mostrar uma mensagem para o usuário
        print(f"Erro ao remover item: {e}")
    return redirect('compra')

def editar_pedido(request, item_id):
    pedido = get_object_or_404(PedidoCompra, id=item_id) # Busca o pedido pelo ID ou retorna 404 se não encontrado
    errors = [] #armazena os erros

    if request.method == 'POST':
        pedido.fornecedor_id = request.POST.get('fornecedor') 
        pedido.data_pedido = request.POST.get('data_pedido')
        pedido.save()
        # atualiza o fornecedor e a data do pedido


        #recupera os dados dos produtos, quantidades e preços
        produtos = request.POST.get('produtos', '').split(',')
        quantidades = request.POST.get('quantidades', '').split(',')
        precos_unitarios = request.POST.get('precos_unitarios', '').split(',')

        if len(produtos) == len(quantidades) == len(precos_unitarios):
            # Restaurar o estoque dos produtos antigos antes de excluir
            produtos_antigos = PedidoProduto.objects.filter(pedido=pedido)
            for item in produtos_antigos:
                item.produto.estoque -= item.quantidade  # Subtrair o estoque antigo
                item.produto.save()

            # Excluir os produtos antigos associados ao pedido
            PedidoProduto.objects.filter(pedido=pedido).delete()

            # adiciona os novos produtos e ajusta o estoque
            for prod_id, quantidade, preco_unitario in zip(produtos, quantidades, precos_unitarios):
                try:
                    if not prod_id:
                        continue  # Ignorar se não houver produto

                    produto = Produto.objects.get(id=int(prod_id)) # faz a busca pelo id
                    quantidade = Decimal(quantidade.replace(',', '.'))
                    preco_unitario = Decimal(preco_unitario.replace(',', '.'))

                    # Verificar se a quantidade e o preço são válidos
                    if quantidade <= 0:
                        errors.append(f"A quantidade para o produto '{produto.nome}' deve ser maior que zero.")
                    if preco_unitario < 0:
                        errors.append(f"O preço unitário para o produto '{produto.nome}' não pode ser negativo.")

                    if quantidade > 0 and preco_unitario >= 0:
                        produto.estoque += quantidade  # Adicionar ao estoque
                        produto.save()

                        # Cria a nova associação entre o pedido e o produto
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
            return render(request, 'editar_pedido.html', context)  # Retornar ao formulário de edição

        pedido.calcular_total()
        return redirect('compra')

    context = {
        'pedido': pedido,
        'errors': errors
    }
    #TUDO VALIDAÇÃO OU MENSAGEM DE ERRO!S

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