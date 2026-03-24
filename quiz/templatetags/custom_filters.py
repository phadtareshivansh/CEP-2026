from django import template

register = template.Library()


@register.filter
def dict_lookup(d, key):
    """Look up a key in a dictionary.
    Usage: {{ dict_variable|dict_lookup:key }}
    """
    if d is None:
        return None
    return d.get(key, None) if isinstance(d, dict) else None


@register.filter
def multiply(value, arg):
    """Multiply the value by the argument.
    Usage: {{ value|multiply:2 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """Divide the value by the argument.
    Usage: {{ value|divide:2 }}
    """
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
