
from menu.models import MenuItem

from django import template
from django.urls import resolve

register = template.Library()


@register.inclusion_tag('menu.html')
def draw_menu(menu_name, request):
    menu_items = MenuItem.objects.select_related('parent')
    active_url = 'http://127.0.0.1:8000'+request.path
    print(active_url)
    active_item = None
    ancestors = list()

    for item in menu_items:
        print(item)
        if item.url == active_url:
            active_item = item
            current_item = active_item
            while current_item:
                ancestors.append(current_item)
                current_item = current_item.parent
            break
    reverse_ancestors = []
    i = -1
    for item in range(len(ancestors[1:])):
        reverse_ancestors.append(ancestors[i])
        i -= 1
    print({'menu_items': menu_items, 'active_item': active_item, 'ancestors': reverse_ancestors})
    return {'menu_items': menu_items, 'active_item': active_item, 'ancestors': reverse_ancestors, 'enumerat':enumerate(ancestors)}
