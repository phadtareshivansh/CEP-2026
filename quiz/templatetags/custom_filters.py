from django import template
from django.utils.safestring import mark_safe
from datetime import timedelta

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


@register.filter
def commaseparated(value):
    """Format number with comma separators.
    Usage: {{ price|commaseparated }}
    """
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value


@register.filter
def get_key(dictionary, key):
    """Get value from dictionary using key.
    Usage: {{ dict|get_key:key_name }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def add_months(value, months):
    """Add months to a date.
    Usage: {{ date|add_months:3 }}
    """
    from datetime import datetime, timedelta
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d').date()
        except:
            return value
    
    if hasattr(value, 'date'):
        value = value.date()
    
    try:
        months = int(months)
        new_month = value.month + months
        new_year = value.year
        
        while new_month > 12:
            new_month -= 12
            new_year += 1
        
        while new_month < 1:
            new_month += 12
            new_year -= 1
        
        # Handle day overflow (e.g., Jan 31 + 1 month)
        import calendar
        max_day = calendar.monthrange(new_year, new_month)[1]
        new_day = min(value.day, max_day)
        
        return datetime(new_year, new_month, new_day).date()
    except:
        return value
