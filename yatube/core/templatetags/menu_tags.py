from menu.models import MenuItem
from django import template

register = template.Library()


@register.inclusion_tag('menu.html')
def draw_menu(menu_name, request):
    menu_items = MenuItem.objects.select_related('parent')  # выбираем все элементы меню с их родительскими элементами
    active_url = 'http://127.0.0.1:8000' + request.path  # формируем активный URL из запроса
    print(active_url)  # выводим активный URL в консоль (для отладки)
    active_item = None  # инициализируем активный элемент как None
    ancestors = list()  # создаем пустой список для предков

    # проходимся по всем элементам меню
    for item in menu_items:
        print(item)  # выводим каждый элемент меню в консоль (для отладки)
        if item.url == active_url:  # если URL элемента совпадает с активным URL
            active_item = item  # устанавливаем текущий элемент как активный
            current_item = active_item  # устанавливаем текущий элемент как текущий активный элемент
            while current_item:  # продолжаем цикл, пока текущий элемент существует
                ancestors.append(current_item)  # добавляем текущий элемент в список предков
                current_item = current_item.parent  # устанавливаем текущим элементом его родителя
            break  # выходим из цикла

    # не работал reverse()

    reverse_ancestors = []  # создаем пустой список для реверса предков
    i = -1  # начинаем с последнего элемента в списке
    for item in range(len(ancestors[1:])):  # проходим по всем элементам предков, начиная с первого
        reverse_ancestors.append(ancestors[i])  # добавляем элемент в список реверса
        i -= 1  # уменьшаем индекс для перехода к предыдущему элементу

    # возвращаем словарь с данными для шаблона
    return {'menu_items': menu_items, 'active_item': active_item, 'ancestors': reverse_ancestors}
