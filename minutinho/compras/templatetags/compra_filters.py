from django import template
import re

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except (TypeError, ValueError):
        return ''

@register.filter(name='formatar_cpf')
def formatar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)  # Remove qualquer caractere não numérico
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}" if len(cpf) == 11 else cpf

@register.filter(name='formatar_cnpj')
def formatar_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', cnpj)  # Remove qualquer caractere não numérico
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}" if len(cnpj) == 14 else cnpj