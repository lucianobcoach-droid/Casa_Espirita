from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def br_money(value: object) -> str:
    try:
        decimal_value = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        formatted_number = '0,00'
    else:
        formatted_number = f'{decimal_value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    return formatted_number
