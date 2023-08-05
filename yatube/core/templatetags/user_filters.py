# core/templatetags/user_filters.py
from django import template

# В template.Library зарегистрированы все встроенные теги и фильтры шаблонов;
# добавляем к ним и наш фильтр.
register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


# синтаксис @register... , под который описана функция addclass() -
# это применение "декораторов", функций, меняющих поведение функций

@register.filter
def uglify(text):
    text2 = ''
    for letter in range(len(str(text))):
        if letter == 0 or letter % 2 == 0:
            text2 = text2 + text[letter].lower()
        else:
            text2 = text2 + text[letter].upper()
    return text2
