from django import template

register = template.Library()


@register.simple_tag
def querystring(request, **kwargs):
    """
    Return current querystring with updated keys.
    Empty values remove a key from the query.
    """
    query = request.GET.copy()
    for key, value in kwargs.items():
        if value in (None, ""):
            query.pop(key, None)
        else:
            query[key] = value

    encoded = query.urlencode()
    return f"?{encoded}" if encoded else ""


@register.filter
def get_item(mapping, key):
    if isinstance(mapping, dict):
        return mapping.get(key)
    return None
