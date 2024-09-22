from django import template

register = template.Library()

@register.filter
def valor_geral(pedidos):
    total = sum(pedido.valor_total for pedido in pedidos)
    return total

@register.filter
def formatar_cpf(cpf):
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

@register.filter
def formatar_telefone(telefone):
    telefone = telefone.replace(" ", "").replace("-", "")  
    if len(telefone) == 11:  # Formato para números móveis
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    return telefone

@register.filter
def quantidade_total(itens):
    return sum(item.quantidade for item in itens)