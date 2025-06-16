from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return float(value) * float(arg)

@register.filter
def divide(value, arg):
    return float(value) / float(arg)

@register.filter
def subtract(value, arg):
    return float(value) - float(arg)

@register.filter
def add_days(value, arg):
    from datetime import timedelta
    return value + timedelta(days=arg)

@register.filter(name='times')
def times(number):
    return range(1, number + 1)