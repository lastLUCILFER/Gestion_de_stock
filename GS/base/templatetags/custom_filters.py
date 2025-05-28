from django import template
from base.models import Client

register = template.Library()

@register.filter
def get_client(user_id):
    try:
        return Client.objects.get(id=user_id)
    except Client.DoesNotExist:
        return None 