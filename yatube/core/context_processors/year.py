from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year': datetime.today().year
    }

# def welcome(request):
#     """Добавляет в контекст переменную greeting с приветствием."""
#     return {
#         'greeting': 'Ennyn Pronin: pedo mellon a minno.',
#         }

# {# Например, в навигации #}
#
# {% if user.is_authenticated %}
#   {# Авторизованному пользователю покажем ссылки на выход и смену пароля #}
# {% else %}
#   {# Неавторизованному покажем ссылки на регистрацию и авторизацию #}
# {% endif %}


# {# Код HTML-шаблона #}
# ...и на Вратах было начертано: <b>{{ greeting }}</b>
