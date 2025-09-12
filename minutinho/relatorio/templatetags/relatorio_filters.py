from django import template

register = template.Library()

MAPA_PAGAMENTO = {
    "credito": "Cartão de Crédito",
    "debito": "Cartão de Débito",
    "pix": "Pix",
    "boleto": "Boleto Bancário",
    "transferencia": "Transferência Bancária",
    "dinheiro": "Dinheiro",
}

@register.filter
def pagamento_legivel(valor):
    """Converte a sigla de pagamento em nome legível"""
    return MAPA_PAGAMENTO.get(valor, valor)
