import re
from django import template

register = template.Library()

@register.filter(name='formatar_cpf')
def formatar_cpf(cpf):
    cpf = re.sub(r'[^\d]', '', cpf) 
    return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'

@register.filter(name='formatar_telefone')
def formatar_telefone(telefone):
    telefone = re.sub(r'[^\d]', '', telefone) 
    return f'({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}'
