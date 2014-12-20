from django.contrib.humanize.templatetags.humanize import intcomma
from django import template

register = template.Library()

@register.filter(name='ec_val_lookup')
def ec_val_lookup(ec_dict, key):
    if ec_dict.__class__.__name__ == 'dict':
        return ec_dict.get(key, None)
    return None
#register.filter('ec_lookup', ec_lookup)
#{{ mydict|ec_lookup:item.name }}
