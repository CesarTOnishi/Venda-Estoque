from django import template

register = template.Library()

# Dicionário com os métodos de pagamento
TIPOS_PAGAMENTO = {
    'boleto': 'Boleto Bancário',
    'pix': 'PIX',
    'cartao': 'Cartão de Crédito',
    'dinheiro': 'Dinheiro',
    'transferencia': 'Transferência Bancária',
    'credito': 'Cartão de Crédito',
    'debito': 'Cartão de Débido',
    'cartao_credito': 'Cartão de Crédito',
}

@register.filter
def metodo_pagamento_label(codigo):
    """
    Retorna o nome legível do método de pagamento a partir do código.
    Ex: 'boleto' => 'Boleto Bancário'
    """
    return TIPOS_PAGAMENTO.get(codigo, 'Desconhecido')
