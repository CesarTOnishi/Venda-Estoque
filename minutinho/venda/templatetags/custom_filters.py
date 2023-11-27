from django import template

register = template.Library()

@register.filter
def valor_geral(pedidos):
    total = sum(pedido.valor_total for pedido in pedidos)
    return total