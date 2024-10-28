# ventas/templatetags/ventas_extras.py

from django import template

register = template.Library()

@register.filter
def formato_clp(value):
    """
    Formatea un número como CLP con separadores de miles y el símbolo de pesos.
    Ejemplo: 1762000 -> $1.762.000
    """
    try:
        value = float(value)
        # Formatear con separadores de miles y sin decimales
        formatted = "{:,.0f}".format(value).replace(",", ".")
        return f"${formatted}"
    except (ValueError, TypeError):
        return value  # Retorna el valor original si hay un error
