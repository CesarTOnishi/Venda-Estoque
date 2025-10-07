from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from .models import Extrato, ContaReceber, ContaPagar, ContaBancaria, MovimentacaoBancaria
from datetime import date
from django.contrib.auth.decorators import login_required
from fornecedor.functions import removerFornecedor
from django.contrib import messages
import re
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from django.utils import timezone
from condicaoPagamento.models import CondicaoPagamento
from django.utils.dateparse import parse_date
import datetime
from django.db.models import Q
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from decimal import Decimal
from django.db import models                

@login_required(login_url="/login/")
def contasReceber(request):
    todas_contas = ContaReceber.objects.all()
    contas_receber = ContaReceber.objects.all().order_by('-criado_em')
    extratos_pagos = Extrato.objects.filter(status='pago')
    pagamentos = CondicaoPagamento.objects.all().order_by('-id')
    tipos_pagamento = dict(CondicaoPagamento.TIPO_PAGAMENTO_CHOICES)
    hoje = date.today()

    search_query = request.GET.get('search', '')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    vencimento_inicio = request.GET.get('vencimento_inicio')
    vencimento_fim = request.GET.get('vencimento_fim')
    status = request.GET.get('status')
    metodo = request.GET.get('metodo')
    valor_min = request.GET.get('valor_min')
    valor_max = request.GET.get('valor_max')

    total_contas = todas_contas.count()
    contas_pendentes = todas_contas.filter(recebido=False).count()
    contas_recebidas = todas_contas.filter(recebido=True).count()
    contas_vencidas = todas_contas.filter(data_vencimento__lt=hoje, recebido=False).count()

    if search_query:
        if search_query.isdigit():
            contas_receber = contas_receber.filter(Q(id=search_query) | Q(descricao__icontains=search_query))
        else:
            contas_receber = contas_receber.filter(descricao__icontains=search_query)

    if data_inicio and data_fim:
        contas_receber = contas_receber.filter(
            criado_em__date__gte=data_inicio,
            criado_em__date__lte=data_fim
        )
    elif data_inicio:
        contas_receber = contas_receber.filter(criado_em__date__gte=data_inicio)
    elif data_fim:
        contas_receber = contas_receber.filter(criado_em__date__lte=data_fim)

    if vencimento_inicio and vencimento_fim:
        contas_receber = contas_receber.filter(
            data_vencimento__gte=vencimento_inicio,
            data_vencimento__lte=vencimento_fim
        )
    elif vencimento_inicio:
        contas_receber = contas_receber.filter(data_vencimento__gte=vencimento_inicio)
    elif vencimento_fim:
        contas_receber = contas_receber.filter(data_vencimento__lte=vencimento_fim)

    if status == 'pago':
        contas_receber = contas_receber.filter(recebido=True)
    elif status == 'pendente':
        contas_receber = contas_receber.filter(recebido=False)
    elif status == 'vencido':
        hoje = date.today()
        contas_receber = contas_receber.filter(data_vencimento__lt=hoje, recebido=False)

    if metodo:
        contas_receber = contas_receber.filter(metodo_pagamento=metodo)

    if valor_min:
        contas_receber = contas_receber.filter(valor__gte=float(valor_min))
    
    if valor_max:
        contas_receber = contas_receber.filter(valor__lte=float(valor_max))

    saldo_total = sum(
        extrato.valor if extrato.tipo == 'entrada' else -extrato.valor
        for extrato in extratos_pagos
    )
    
    paginator = Paginator(contas_receber, 10)  # 10 itens por página
    page_number = request.GET.get('page')
    contas_paginadas = paginator.get_page(page_number)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        contas_list = []
        for conta in contas_paginadas:
            vencida = conta.data_vencimento < hoje and not conta.recebido
            contas_list.append({
                'id': conta.id,
                'descricao': conta.descricao,
                'valor': str(conta.valor),
                'metodo_pagamento': conta.get_metodo_pagamento_display(),
                'vencimento': conta.data_vencimento.strftime('%d/%m/%Y'),
                'criado_em': conta.criado_em.strftime('%d/%m/%Y %H:%M'),  # Adicionado
                'status': 'Pago' if conta.recebido else 'Pendente',
                'editavel': conta.editavel,
                'vencida': vencida,  # Adicionado
                'recebido': conta.recebido  # Adicionado para o select
            })
        
        return JsonResponse({
            'contas': contas_list,
            'paginator': {
                'num_pages': contas_paginadas.paginator.num_pages,
                'number': contas_paginadas.number,
                'has_previous': contas_paginadas.has_previous(),
                'has_next': contas_paginadas.has_next(),
                'previous_page_number': contas_paginadas.previous_page_number() if contas_paginadas.has_previous() else None,
                'next_page_number': contas_paginadas.next_page_number() if contas_paginadas.has_next() else None,
            },
            'saldo_total': saldo_total  # Adicionado para atualizar o saldo
        })

    if request.method == "POST":
        pagamento_id = request.POST.get('pagamento_id') 
        metodo_pagamento = request.POST.get('tipo_pagamento')
        descricao = request.POST.get('descricao')
        vencimento = request.POST.get('vencimento')
        valor = request.POST.get('valor')

        form_data = {
            'tipo_pagamento': metodo_pagamento,
            'descricao': descricao,
            'vencimento': vencimento,
            'valor': valor
        }

        errors = []

        if not descricao or not metodo_pagamento or not vencimento or not valor:
            errors.append("Todos os campos são obrigatórios.")
        else:
            try:
                valor_float = float(valor)

                if pagamento_id:
                    conta = get_object_or_404(ContaReceber, id=pagamento_id)

                    if not conta.editavel:
                        errors.append("Esta conta não pode ser editada.")
                    else:
                        conta.descricao = descricao
                        conta.metodo_pagamento = metodo_pagamento
                        conta.data_vencimento = vencimento
                        conta.valor = valor_float
                        conta.save()
                        messages.success(request, "Conta a receber atualizada com sucesso.")
                        return redirect('contasReceber')
                else:
                    ContaReceber.objects.create(
                        descricao=descricao,
                        valor=valor_float,
                        metodo_pagamento=metodo_pagamento,
                        data_vencimento=vencimento,
                        recebido=False,
                        numero_parcela=1,
                        editavel=True,
                    )
                    messages.success(request, "Conta a receber adicionada com sucesso.")
                    return redirect('contasReceber')

            except CondicaoPagamento.DoesNotExist:
                errors.append("Forma de pagamento inválida.")
            except Exception as e:
                errors.append(f"Ocorreu um erro ao salvar: {str(e)}")

        context = {
            'contas': contas_paginadas,
            'saldo_total': saldo_total,
            'errors': errors,
            'form_data': form_data,
            'tipos_pagamento': tipos_pagamento,
            'pagamentos': pagamentos,
            'total_contas': total_contas,
            'contas_pendentes': contas_pendentes,
            'contas_recebidas': contas_recebidas,
            'contas_vencidas': contas_vencidas,
        }
        return render(request, 'contareceber.html', context)

    context = {
        'contas': contas_paginadas,
        'saldo_total': saldo_total,
        'pagamentos': pagamentos,
        'tipos_pagamento': tipos_pagamento,
        'total_contas': total_contas,
        'contas_pendentes': contas_pendentes,
        'contas_recebidas': contas_recebidas,
        'contas_vencidas': contas_vencidas,
    }
    return render(request, 'contareceber.html', context)

@login_required(login_url="/login/")
def contasPagar(request):
    todas_contas = ContaPagar.objects.all()
    contas_pagar = ContaPagar.objects.all().order_by('-criacao')
    extratos_pagos = Extrato.objects.filter(status='pago')
    pagamentos = CondicaoPagamento.objects.all().order_by('-id')
    tipos_pagamento = dict(CondicaoPagamento.TIPO_PAGAMENTO_CHOICES)
    hoje = date.today()

    total_contas = todas_contas.count()
    contas_pendentes = todas_contas.filter(pago=False).count()
    contas_pagas = todas_contas.filter(pago=True).count()
    contas_vencidas = todas_contas.filter(data_vencimento__lt=hoje, pago=False).count()
    search_query = request.GET.get('search', '')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    vencimento_inicio = request.GET.get('vencimento_inicio')
    vencimento_fim = request.GET.get('vencimento_fim')
    status = request.GET.get('status')
    metodo = request.GET.get('metodo')
    valor_min = request.GET.get('valor_min')
    valor_max = request.GET.get('valor_max')

    if search_query:
        if search_query.isdigit():
            contas_pagar = contas_pagar.filter(Q(id=search_query) | Q(descricao__icontains=search_query))
        else:
            contas_pagar = contas_pagar.filter(descricao__icontains=search_query)

    if data_inicio and data_fim:
        contas_pagar = contas_pagar.filter(
            criacao__date__gte=data_inicio,
            criacao__date__lte=data_fim
        )
    elif data_inicio:
        contas_pagar = contas_pagar.filter(criacao__date__gte=data_inicio)
    elif data_fim:
        contas_pagar = contas_pagar.filter(criacao__date__lte=data_fim)

    if vencimento_inicio and vencimento_fim:
        contas_pagar = contas_pagar.filter(
            data_vencimento__gte=vencimento_inicio,
            data_vencimento__lte=vencimento_fim
        )
    elif vencimento_inicio:
        contas_pagar = contas_pagar.filter(data_vencimento__gte=vencimento_inicio)
    elif vencimento_fim:
        contas_pagar = contas_pagar.filter(data_vencimento__lte=vencimento_fim)

    if status == 'pago':
        contas_pagar = contas_pagar.filter(pago=True)
    elif status == 'pendente':
        contas_pagar = contas_pagar.filter(pago=False)
    elif status == 'vencido':
        contas_pagar = contas_pagar.filter(data_vencimento__lt=hoje, pago=False)

    if metodo:
        contas_pagar = contas_pagar.filter(metodo_pagamento=metodo)

    if valor_min:
        contas_pagar = contas_pagar.filter(valor__gte=float(valor_min))
    
    if valor_max:
        contas_pagar = contas_pagar.filter(valor__lte=float(valor_max))

    saldo_total = sum(
        extrato.valor if extrato.tipo == 'entrada' else -extrato.valor
        for extrato in extratos_pagos
    )
    
    # Paginação
    paginator = Paginator(contas_pagar, 10)  # 10 itens por página
    page_number = request.GET.get('page')
    contas_paginadas = paginator.get_page(page_number)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        contas_list = []
        for conta in contas_paginadas:
            vencida = conta.data_vencimento < hoje and not conta.pago
            contas_list.append({
                'id': conta.id,
                'descricao': conta.descricao,
                'valor': str(conta.valor),
                'metodo_pagamento': conta.get_metodo_pagamento_display(),
                'vencimento': conta.data_vencimento.strftime('%d/%m/%Y'),
                'criado_em': conta.criacao.strftime('%d/%m/%Y %H:%M'),  # Adicionado
                'status': 'Pago' if conta.pago else 'Pendente',
                'editavel': conta.editavel,
                'vencida': vencida,  # Adicionado
                'pago': conta.pago  # Adicionado para o select
            })
        
        return JsonResponse({
            'contas': contas_list,
            'paginator': {
                'num_pages': contas_paginadas.paginator.num_pages,
                'number': contas_paginadas.number,
                'has_previous': contas_paginadas.has_previous(),
                'has_next': contas_paginadas.has_next(),
                'previous_page_number': contas_paginadas.previous_page_number() if contas_paginadas.has_previous() else None,
                'next_page_number': contas_paginadas.next_page_number() if contas_paginadas.has_next() else None,
            },
            'saldo_total': saldo_total  # Adicionado para atualizar o saldo
        })

    if request.method == "POST":
        pagamento_id = request.POST.get('pagamento_id')
        if pagamento_id:
            conta = get_object_or_404(ContaPagar, id=pagamento_id)
            
            if not conta.editavel:
                messages.error(request, "Esta conta não pode ser editada.")
                return redirect('contasPagar')

            metodo_pagamento = request.POST.get('tipo_pagamento')  
            descricao = request.POST.get('descricao') 
            vencimento = request.POST.get('vencimento')
            valor = request.POST.get('valor')
            
            errors = []
            
            if not descricao or not metodo_pagamento or not vencimento or not valor:
                errors.append("Todos os campos são obrigatórios.")
            else:
                try:
                    valor = float(valor)
                    conta.descricao = descricao
                    conta.valor = valor
                    conta.metodo_pagamento = metodo_pagamento
                    conta.data_vencimento = vencimento
                    conta.save()
                    messages.success(request, "Conta a pagar atualizada com sucesso.")
                    return redirect('contasPagar')
                except Exception as e:
                    errors.append(f"Ocorreu um erro ao salvar: {str(e)}")
            
            context = {
                'contas': contas_paginadas,
                'saldo_total': saldo_total,
                'errors': errors,
                'form_data': {
                    'tipo_pagamento': metodo_pagamento,
                    'descricao': descricao,
                    'vencimento': vencimento,
                    'valor': valor,
                    'pagamento_id': pagamento_id
                },
                'tipos_pagamento': tipos_pagamento,
                'pagamentos': pagamentos,
                'total_contas': total_contas,
                'contas_pendentes': contas_pendentes,
                'contas_pagas': contas_pagas,
                'contas_vencidas': contas_vencidas,
            }
            return render(request, 'contapagar.html', context)
        
        # Se não for edição, cria nova conta
        metodo_pagamento = request.POST.get('tipo_pagamento')  
        descricao = request.POST.get('descricao') 
        vencimento = request.POST.get('vencimento')
        valor = request.POST.get('valor')
        
        form_data = {
            'tipo_pagamento': metodo_pagamento, 
            'descricao': descricao,
            'vencimento': vencimento,
            'valor': valor
        }
        
        errors = []

        if not descricao or not metodo_pagamento or not vencimento or not valor:
            errors.append("Todos os campos são obrigatórios.")
        else:
            try:
                valor = float(valor)

                ContaPagar.objects.create(
                    descricao=descricao,
                    valor=valor,
                    metodo_pagamento=metodo_pagamento,
                    data_vencimento=vencimento,
                    pago=False,
                    numero_parcela=1,
                    editavel=True,
                )
                messages.success(request, "Conta a pagar adicionada com sucesso.")
                return redirect('contasPagar')
            
            except CondicaoPagamento.DoesNotExist:
                errors.append("Forma de pagamento inválida.")
            except Exception as e:
                errors.append(f"Ocorreu um erro ao salvar: {str(e)}")

        context = {
            'contas': contas_paginadas,
            'saldo_total': saldo_total,
            'errors': errors,
            'form_data': form_data,
            'tipos_pagamento': tipos_pagamento,
            'pagamentos': pagamentos,
            'total_contas': total_contas,
            'contas_pendentes': contas_pendentes,
            'contas_pagas': contas_pagas,
            'contas_vencidas': contas_vencidas,
        }
        return render(request, 'contapagar.html', context)
    
    context = {
        'contas': contas_paginadas,
        'saldo_total': saldo_total,
        'pagamentos': pagamentos,
        'tipos_pagamento': tipos_pagamento,
        'total_contas': total_contas,
        'contas_pendentes': contas_pendentes,
        'contas_pagas': contas_pagas,
        'contas_vencidas': contas_vencidas,
    }
    return render(request, 'contapagar.html', context)

@login_required(login_url="/login/")
def financeiro(request):
    extratos = Extrato.objects.filter(status='pago').select_related(
        'conta_receber', 'conta_pagar'
    ).order_by('-data_transacao')

    # Filtros
    search_query = request.GET.get('search', '')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    tipo = request.GET.get('tipo')
    status = request.GET.get('status')
    metodo = request.GET.get('metodo')
    valor_min = request.GET.get('valor_min')
    valor_max = request.GET.get('valor_max')

    if search_query:
        extratos = extratos.filter(
            Q(descricao__icontains=search_query) |
            Q(conta_receber__descricao__icontains=search_query) |
            Q(conta_pagar__descricao__icontains=search_query) |
            Q(id__icontains=search_query) |
            Q(conta_receber__pedido__id__icontains=search_query) |  
            Q(conta_pagar__pedido__id__icontains=search_query)
        )

    if data_inicio and data_fim:
        extratos = extratos.filter(
            data_transacao__date__gte=data_inicio,
            data_transacao__date__lte=data_fim
        )
    elif data_inicio:
        extratos = extratos.filter(data_transacao__date__gte=data_inicio)
    elif data_fim:
        extratos = extratos.filter(data_transacao__date__lte=data_fim)

    if tipo:
        extratos = extratos.filter(tipo=tipo)

    if status:
        extratos = extratos.filter(status=status)

    if metodo:
        extratos = extratos.filter(metodo_pagamento=metodo)

    if valor_min:
        extratos = extratos.filter(valor__gte=float(valor_min))
    
    if valor_max:
        extratos = extratos.filter(valor__lte=float(valor_max))

    metodos_pagamento = Extrato.objects.exclude(metodo_pagamento__isnull=True)\
                                      .exclude(metodo_pagamento__exact='')\
                                      .values_list('metodo_pagamento', flat=True)\
                                      .distinct()

    saldo_total = sum(
        extrato.valor if extrato.tipo == 'entrada' else -extrato.valor
        for extrato in extratos
    )

    paginator = Paginator(extratos, 10) 
    page_number = request.GET.get('page')
    extratos_paginados = paginator.get_page(page_number)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        extratos_list = []
        for extrato in extratos_paginados:
            extratos_list.append({
                'id': extrato.id,
                'data': extrato.data_transacao.strftime('%d/%m/%Y %H:%M'),
                'descricao': extrato.descricao,
                'conta_relacionada': {
                    'id': extrato.conta_receber.id if extrato.conta_receber else extrato.conta_pagar.id if extrato.conta_pagar else None,
                    'descricao': extrato.conta_receber.descricao if extrato.conta_receber else extrato.conta_pagar.descricao if extrato.conta_pagar else None,
                    'tipo': 'receber' if extrato.conta_receber else 'pagar' if extrato.conta_pagar else None
                },
                'metodo_pagamento': extrato.metodo_pagamento or '-',
                'valor': str(extrato.valor),
                'tipo': extrato.tipo,
                'status': extrato.get_status_display(),
                'valor_formatado': f"{'+' if extrato.tipo == 'entrada' else '-'} R$ {extrato.valor:.2f}",
                'classe_valor': 'valor-positivo' if extrato.tipo == 'entrada' else 'valor-negativo',
                'classe_status': f'status-{extrato.status}'
            })
        
        return JsonResponse({
            'extratos': extratos_list,
            'paginator': {
                'num_pages': extratos_paginados.paginator.num_pages,
                'number': extratos_paginados.number,
                'has_previous': extratos_paginados.has_previous(),
                'has_next': extratos_paginados.has_next(),
                'previous_page_number': extratos_paginados.previous_page_number() if extratos_paginados.has_previous() else None,
                'next_page_number': extratos_paginados.next_page_number() if extratos_paginados.has_next() else None,
            },
            'saldo_total': saldo_total,
            'metodos_pagamento': list(metodos_pagamento)
        })

    context = {
        'extratos': extratos_paginados,
        'saldo_total': saldo_total,
        'metodos_pagamento': metodos_pagamento,
    }
    
    return render(request, 'extrato.html', context)

@login_required(login_url="/login/")
@require_POST
def atualizarPagamento(request, conta_id):
    conta = get_object_or_404(ContaReceber, id=conta_id)
    novo_status = request.POST.get('status')
    errors = []

    conta.recebido = novo_status == 'pago'
    conta.data_recebimento = timezone.now() if conta.recebido else None
    conta.save()

    descricao_extrato = f"Recebimento: {conta.descricao} (Parcela {conta.numero_parcela})"

    if conta.recebido:
        try:
            Extrato.objects.get_or_create(
                descricao=descricao_extrato,
                valor=conta.valor,
                metodo_pagamento=conta.metodo_pagamento,
                tipo='entrada',
                status='pago',
                data_transacao=timezone.now(),
                conta_receber=conta
            )
        except Exception as e:
            errors.append(f'Erro ao criar o registro no extrato')
            return JsonResponse({
                'success': False,
                'errors': errors,
            })
    else:
        try:
            Extrato.objects.filter(
                conta_receber=conta,
                status='pago'
            ).delete()
        except Exception as e:
            errors.append(f'Erro ao remover o registro do extrato')
            return JsonResponse({
                'success': False,
                'errors': errors,
            })

    saldo_total = sum(
        extrato.valor if extrato.tipo == 'entrada' else -extrato.valor
        for extrato in Extrato.objects.filter(status='pago')
    )

    return JsonResponse({
        'success': True,
        'novo_status': 'pago' if conta.recebido else 'pendente',
        'saldo_total': saldo_total,
    })


@login_required(login_url="/login/")
@require_POST
def atualizarSaldo(request, conta_id):
    conta = get_object_or_404(ContaPagar, id=conta_id)
    novo_status = request.POST.get('status')

    errors = []


    conta.pago = novo_status == 'pago'
    conta.data_pagamento = timezone.now() if conta.pago else None
    conta.save()

    if conta.pago:
        try:
            extrato, created = Extrato.objects.get_or_create(
                descricao=f"Pagamento: {conta.descricao} (Parcela {conta.numero_parcela})",
                valor=conta.valor,
                metodo_pagamento=conta.metodo_pagamento,  
                tipo='saida',
                status='pago',
                data_transacao=timezone.now()
            )
        except Exception as e:
            errors.append('Erro ao criar o registro no extrato')
            return JsonResponse({
                'success': False,
                'errors': errors,
            })

    saldo_total = sum(
        extrato.valor if extrato.tipo == 'entrada' else -extrato.valor
        for extrato in Extrato.objects.filter(status='pago')
    )

    return JsonResponse({
        'success': True,
        'novo_status': 'pago' if conta.pago else 'pendente',
        'saldo_total': saldo_total,
    })


@login_required(login_url="/login/")
@require_POST
def atualizarPagamentoPagar(request, conta_id):
    conta = get_object_or_404(ContaPagar, id=conta_id)
    novo_status = request.POST.get('status')

    errors = []
    conta.pago = novo_status == 'pago'
    conta.data_pagamento = timezone.now() if conta.pago else None
    conta.save()

    if conta.pago:
        try:
            Extrato.objects.get_or_create(
                conta_pagar=conta,
                descricao=f"Pagamento: {conta.descricao} (Parcela {conta.numero_parcela})",
                valor=conta.valor,
                metodo_pagamento=conta.metodo_pagamento,
                tipo='saida',
                status='pago',
                data_transacao=timezone.now()
            )
        except Exception as e:
            errors.append('Erro ao criar o registro no extrato')
            return JsonResponse({
                'success': False,
                'errors': errors,
            })
    else:
        try:
            Extrato.objects.filter(
                conta_pagar=conta,
                status='pago'
            ).delete()
        except Exception as e:
            errors.append('Erro ao remover o registro do extrato')
            return JsonResponse({
                'success': False,
                'errors': errors,
            })

    saldo_total = sum(
        extrato.valor if extrato.tipo == 'entrada' else -extrato.valor
        for extrato in Extrato.objects.filter(status='pago')
    )

    return JsonResponse({
        'success': True,
        'novo_status': 'pago' if conta.pago else 'pendente',
        'saldo_total': saldo_total,
    })

@login_required
@require_GET
def detalhes_conta(request, tipo_conta, conta_id):
    if tipo_conta == 'receber':
        conta = get_object_or_404(ContaReceber, id=conta_id)
        metodo_pagamento = conta.metodo_pagamento  
        
        data = {
            'success': True,
            'descricao': conta.descricao,
            'valor': f"{conta.valor:.2f}",
            'metodo_pagamento': metodo_pagamento,
            'data_vencimento': conta.data_vencimento.strftime('%d/%m/%Y'),
            'status': 'Recebido' if conta.recebido else 'Pendente',
            'pedido': f"Pedido #{conta.pedido.id}" if conta.pedido else None,
            'data_criacao': conta.criado_em.strftime('%d/%m/%Y %H:%M'),
        }
    elif tipo_conta == 'pagar':
        conta = get_object_or_404(ContaPagar, id=conta_id)
        data = {
            'success': True,
            'descricao': conta.descricao,
            'valor': f"{conta.valor:.2f}",
            'metodo_pagamento': conta.metodo_pagamento,
            'data_vencimento': conta.data_vencimento.strftime('%d/%m/%Y'),
            'status': 'Pago' if conta.pago else 'Pendente',
            'pedido': f"Pedido Compra #{conta.pedido.id}" if conta.pedido else None,
            'data_criacao': conta.criacao.strftime('%d/%m/%Y %H:%M'),
        }
    else:
        data = {'success': False, 'error': 'Tipo de conta inválido'}
    
    return JsonResponse(data)


@login_required(login_url='/login/')
def contaBancaria(request):
    contas = ContaBancaria.objects.all().order_by('banco')
    erros = []

    if request.method == "POST":
        conta_id = request.POST.get("conta_id")
        nome = request.POST.get("nome")
        banco = request.POST.get("banco")
        tipo_conta = request.POST.get("tipo_conta")
        numero_conta = request.POST.get("numero_conta")
        agencia = request.POST.get("agencia")
        saldo_inicial = request.POST.get("saldo_inicial") or 0
        ativo = request.POST.get("ativo") == "True"

        if not banco or not tipo_conta:
            erros.append("Preencha todos os campos obrigatórios.")
        else:
            if conta_id:
                conta = get_object_or_404(ContaBancaria, id=conta_id)
            else:
                conta = ContaBancaria()

            conta.banco = banco
            conta.nome = nome
            conta.tipo_conta = tipo_conta
            conta.numero_conta = numero_conta
            conta.agencia = agencia
            conta.saldo_inicial = saldo_inicial
            conta.ativo = ativo
            conta.save()
            return redirect('contaBancaria')

    tipos_conta = dict(ContaBancaria.TIPO_CONTA_CHOICES)

    context = {
        'contas': contas,
        'tipos_conta': tipos_conta,
        'errors': erros,
    }
    return render(request, 'conta.html', context)


@login_required(login_url='/login/')
def deletarConta(request, id):
    conta = get_object_or_404(ContaBancaria, id=id)
    conta.delete()
    return redirect('contaBancaria')


@login_required(login_url='/login/')
def alternarAtivo(request, id):
    conta = get_object_or_404(ContaBancaria, id=id)
    conta.ativo = not conta.ativo
    conta.save()
    return redirect('contaBancaria')

@login_required(login_url='/login/')
def movimentacoes(request, conta_id):
    conta = get_object_or_404(ContaBancaria, id=conta_id)
    movimentacoes = conta.movimentacoes.order_by('-data')

    saldo_total = conta.saldo_inicial
    hoje = timezone.now()
    movimentacoes_mes = movimentacoes.filter(data__month=hoje.month, data__year=hoje.year)
    total_entradas_mes = movimentacoes_mes.filter(tipo='entrada').aggregate(total=models.Sum('valor'))['total'] or 0
    total_saidas_mes = movimentacoes_mes.filter(tipo='saida').aggregate(total=models.Sum('valor'))['total'] or 0

    if request.method == 'POST':
        descricao = request.POST.get('descricao')
        tipo = request.POST.get('tipo')
        valor = Decimal(request.POST.get('valor') or 0)
        MovimentacaoBancaria.objects.create(conta=conta, descricao=descricao, tipo=tipo, valor=valor)
        return redirect('movimentacoes', conta_id=conta.id)

    context = {
        'conta': conta,
        'movimentacoes': movimentacoes,
        'saldo_total': saldo_total,
        'total_entradas_mes': total_entradas_mes,
        'total_saidas_mes': total_saidas_mes,
    }
    return render(request, 'movimentacao.html', context)
