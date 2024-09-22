import re
from django import template

register = template.Library()

@register.filter
def formatar_cpf(cpf):
    if cpf is None:
        return "Não disponivel"
    if cpf and len(cpf) == 11:
        return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
    return cpf

@register.filter
def formatar_cnpj(cnpj):
    if cnpj is None:
        return "Não disponível"
    cnpj = re.sub(r'[^\d]', '', cnpj)
    if len(cnpj) == 14:
        return '{}.{}.{}/{}-{}'.format(cnpj[:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:])
    return cnpj
