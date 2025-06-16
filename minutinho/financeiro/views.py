from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from .models import Extrato, ContaReceber, ContaPagar
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



@login_required(login_url="/login/")
def contasReceber(request):
    pagamentos = CondicaoPagamento.objects.all().order_by('-id')
    tipos_pagamento = dict(CondicaoPagamento.TIPO_PAGAMENTO_CHOICES)
    contas_receber = ContaReceber.objects.all().order_by('-criado_em')
    extratos_pagos = Extrato.objects.filter(status='pago')
    ano_atual = datetime.date.today().year
    meses_filtro = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }


    saldo_total = sum(
        extrato.valor if extrato.tipo == 'entrada' else -extrato.valor
        for extrato in extratos_pagos
    )

    mes = request.GET.get('mes')
    ano = request.GET.get('ano')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    status = request.GET.get('status') 
    recebido = request.GET.get('recebido')

    if recebido is not None:
        contas_receber = contas_receber.filter(recebido=(recebido == 'true'))

    if status == 'pago':
        contas_receber = contas_receber.filter(recebido=True)
    elif status == 'pendente':
        contas_receber = contas_receber.filter(recebido=False)
    elif status == 'vencido':
        hoje = datetime.date.today()
        contas_receber = contas_receber.filter(data_vencimento__lt=hoje, recebido=False)

    if ano:
            contas_receber = contas_receber.filter(data_vencimento__year=ano)
    if mes:
            contas_receber = contas_receber.filter(data_vencimento__month=mes)

    if data_inicio or data_fim:
        try:
            if data_inicio:
                data_inicio_obj = parse_date(data_inicio)
                if data_inicio_obj:
                    contas_receber = contas_receber.filter(data_vencimento__gte=data_inicio_obj)
            
            if data_fim:
                data_fim_obj = parse_date(data_fim)
                if data_fim_obj:
                    contas_receber = contas_receber.filter(data_vencimento__lte=data_fim_obj)
        except:
            messages.error(request, "Formato de data inválido")

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
                        editavel= True,
                    )
                    messages.success(request, "Conta a receber adicionada com sucesso.")
                    return redirect('contasReceber')

            except CondicaoPagamento.DoesNotExist:
                errors.append("Forma de pagamento inválida.")
            except Exception as e:
                errors.append(f"Ocorreu um erro ao salvar: {str(e)}")

        context = {
            'contas': contas_receber,
            'saldo_total': saldo_total,
            'errors': errors,
            'form_data': form_data,
            'tipos_pagamento': tipos_pagamento,
            'pagamentos': pagamentos,
            'meses_filtro': meses_filtro,
            'mes_selecionado': int(mes) if mes else None,
            'ano_selecionado': int(ano) if ano else None,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'ano_atual_para_filtro': ano_atual,
            'recebido_selecionado': recebido,
            'status_selecionado': status,
            'hoje': datetime.date.today().isoformat(),
        }
        return render(request, 'contareceber.html', context)

    context = {
        'contas': contas_receber,
        'saldo_total': saldo_total,
        'pagamentos': pagamentos,
        'tipos_pagamento': tipos_pagamento,
        'meses_filtro': meses_filtro,
        'mes_selecionado': int(mes) if mes else None,
        'ano_selecionado': int(ano) if ano else None,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'ano_atual_para_filtro': ano_atual,
        'recebido_selecionado': recebido,
        'status_selecionado': status,
        'hoje': datetime.date.today().isoformat(),
    }
    return render(request, 'contareceber.html', context)



@login_required(login_url="/login/")
def contasPagar(request):
    contas_pagar = ContaPagar.objects.all().order_by('-criacao')
    extratos_pagos = Extrato.objects.filter(status='pago')
    pagamentos = CondicaoPagamento.objects.all().order_by('-id')
    tipos_pagamento = dict(CondicaoPagamento.TIPO_PAGAMENTO_CHOICES)

    saldo_total = sum(
        extrato.valor if extrato.tipo == 'entrada' else -extrato.valor
        for extrato in extratos_pagos
    )
    
    if request.method == "POST":
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

                conta = ContaPagar.objects.create(
                    descricao=descricao,
                    valor=valor,
                    metodo_pagamento=metodo_pagamento,
                    data_vencimento=vencimento,
                    pago=False,
                    numero_parcela=1,
                    editavel=False,
                )
                messages.success(request, "Conta a receber adicionada com sucesso.")
                return redirect('contasPagar')
            
            except CondicaoPagamento.DoesNotExist:
                errors.append("Forma de pagamento inválida.")
            except Exception as e:
                errors.append(f"Ocorreu um erro ao salvar: {str(e)}")

        context = {
            'contas': contas_pagar,
            'saldo_total': saldo_total,
            'errors': errors,
            'form_data': form_data,
            'tipos_pagamento': tipos_pagamento,
            'pagamentos': pagamentos,
        }
        return render(request, 'contapagar.html', context)
    
    context = {
        'contas': contas_pagar,
        'saldo_total': saldo_total,
        'pagamentos': pagamentos,
        'tipos_pagamento': tipos_pagamento,
    }
    return render(request, 'contapagar.html', context)

@login_required(login_url="/login/")
def financeiro(request):
    extratos_pagos = Extrato.objects.filter(status='pago').order_by('-data_transacao')
    contas_receber = ContaReceber.objects.all()
    contas_pagar = ContaPagar.objects.all()

    saldo_total = sum(
        extrato.valor if extrato.tipo == 'entrada' else -extrato.valor
        for extrato in extratos_pagos
    )

    context = {
        'contas_pagar': contas_pagar,
        'extratos': extratos_pagos, 
        'contas': contas_receber,   
        'saldo_total': saldo_total,
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
                data_transacao=timezone.now()
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
                descricao=descricao_extrato,
                valor=conta.valor,
                metodo_pagamento=conta.metodo_pagamento,
                tipo='entrada',
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
                descricao=f"Pagamento: {conta.descricao} (Parcela {conta.numero_parcela})",
                valor=conta.valor,
                metodo_pagamento=conta.metodo_pagamento,
                tipo='saida',
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
