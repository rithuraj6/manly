from django import template


register = template.Library()

@register.filter
def inr(value):
    
    try :
        return f"₹{value:,.2f}"
    
    
    except Exception:
        return value