from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import re
from .models import CondicaoPagamento
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse



@login_required(login_url="/login/")
def condicaoPagamento(request):
    pagamentos = CondicaoPagamento.objects.all().order_by('-id')
    tipos_pagamento = dict(CondicaoPagamento.TIPO_PAGAMENTO_CHOICES)

    if request.method == "POST":
        pagamento_id = request.POST.get('pagamento_id', '').strip()
        form_data = {
            'nome': request.POST.get('nome', '').strip(),
            'tipo_pagamento': request.POST.get('tipo_pagamento'),
            'parcelas': request.POST.get('parcelas'),
            'juros': request.POST.get('juros'),
            'intervalo_parcelas': request.POST.get('intervalo_parcelas'),
            'desconto': request.POST.get('desconto')
        }

        errors = []
        if not form_data['nome']:
            errors.append("O nome é obrigatório.")
        elif len(form_data['nome']) > 100:
            errors.append("O nome deve ter no máximo 100 caracteres.")

        if not form_data['tipo_pagamento'] or form_data['tipo_pagamento'] not in tipos_pagamento:
            errors.append("Selecione um tipo de pagamento válido.")

        try:
            form_data['parcelas'] = int(form_data['parcelas'])
            if form_data['parcelas'] <= 0:
                errors.append("O número de parcelas deve ser positivo.")
        except (ValueError, TypeError):
            errors.append("Número de parcelas inválido.")

        try:
            form_data['juros'] = float(form_data['juros'])
            if form_data['juros'] < 0:
                errors.append("Os juros não podem ser negativos.")
        except (ValueError, TypeError):
            errors.append("Valor de juros inválido.")

        try:
            form_data['intervalo_parcelas'] = int(form_data['intervalo_parcelas'])
            if form_data['intervalo_parcelas'] <= 0:
                errors.append("O intervalo entre parcelas deve ser positivo.")
        except (ValueError, TypeError):
            errors.append("Intervalo entre parcelas inválido.")

        try:
            form_data['desconto'] = float(form_data['desconto'])
            if form_data['desconto'] < 0:
                errors.append("O desconto não pode ser negativo.")
        except (ValueError, TypeError):
            errors.append("Valor de desconto inválido.")

        if not errors:
            if pagamento_id:
                condicao = get_object_or_404(CondicaoPagamento, id=pagamento_id)

                condicao_existente = CondicaoPagamento.objects.filter(nome=form_data['nome']).exclude(id=pagamento_id).first()
                
                if condicao_existente:
                    errors.append("Já existe uma condição de pagamento com este nome.")
                else:
                    condicao.tipo_pagamento = form_data['tipo_pagamento']
                    condicao.parcelas = form_data['parcelas']
                    condicao.juros = form_data['juros']
                    condicao.intervalo_parcelas = form_data['intervalo_parcelas']
                    condicao.desconto = form_data['desconto']
                    condicao.save()
                    
                    messages.success(request, "Condição de pagamento atualizada com sucesso!")
                    return redirect('condicaoPagamento')

            else: 
                if CondicaoPagamento.objects.filter(nome=form_data['nome']).exists():
                    errors.append("Já existe uma condição de pagamento com este nome.")
                else:
                    try:
                        nova_condicao = CondicaoPagamento(
                            nome=form_data['nome'],
                            tipo_pagamento=form_data['tipo_pagamento'],
                            parcelas=form_data['parcelas'],
                            juros=form_data['juros'],
                            intervalo_parcelas=form_data['intervalo_parcelas'],
                            desconto=form_data['desconto']
                        )
                        nova_condicao.save()

                        messages.success(request, "Condição de pagamento cadastrada com sucesso!")
                        return redirect('condicaoPagamento')

                    except Exception as e:
                        errors.append(f"Erro ao salvar no banco de dados: {str(e)}")

        context = {
            'pagamentos': pagamentos,
            'tipos_pagamento': tipos_pagamento,
            'errors': errors,
            'form_data': form_data,
            'modal_open': True 
        }
        return render(request, 'condicaoPagamento.html', context)

    return render(request, 'condicaoPagamento.html', {
        'pagamentos': pagamentos,
        'tipos_pagamento': tipos_pagamento
    })

def filtroPagamento(request):
    tipo = request.GET.get("tipo_pagamento")
    pagamentos = CondicaoPagamento.objects.all()

    if tipo:
        pagamentos = pagamentos.filter(tipo_pagamento=tipo)

    lista = []
    for pag in pagamentos:
        lista.append({
            "id": pag.id,
            "tipo_pagamento": pag.tipo_pagamento,
            "tipo_pagamento_display": pag.get_tipo_pagamento_display(),
            "nome": pag.nome,
            "parcelas": pag.parcelas,
            "juros": float(pag.juros),
            "intervalo_parcelas": pag.intervalo_parcelas,
            "desconto": float(pag.desconto),
            "data_criacao": pag.data_criacao.strftime("%d/%m/%Y"),
            "data_atualizacao": pag.data_atualizacao.strftime("%d/%m/%Y")
        })

    return JsonResponse({"pagamentos": lista})