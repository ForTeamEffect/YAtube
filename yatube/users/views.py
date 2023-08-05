from django.shortcuts import render
# from django.contrib.auth.views import PasswordChangeView
# Create your views here.

# library/views.py

# from django.core.mail import send_mail
# users/views.py
# Импортируем CreateView, чтобы создать ему наследника
from django.views.generic import CreateView

# Функция reverse_lazy позволяет получить URL по параметрам функции path()
# Берём, тоже пригодится
from django.urls import reverse_lazy

# Импортируем класс формы, чтобы сослаться на неё во view-классе
from .forms import CreationForm
from django.core.mail import send_mail


class SignUp(CreateView):
    form_class = CreationForm
    # После успешной регистрации перенаправляем пользователя на главную.
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


# class PasswordChangeV(PasswordChangeView):
#     success_url = reverse_lazy('password_change_done')
#     template_name = 'users/password_change_form.html'

def ty_registration(request):
    render(request, 'users/ty_registration.html')


def send_msg(
        email, name, title, artist, date, genre, price, comment,
):
    subject = f"Обмен {artist}-{title} ({date})"
    body = f"""Предложение на обмен диска от {name} ({email})

    Название: {title}
    Исполнитель: {artist}
    Жанр: {genre}
    Дата выпуска альбома: {date}
    Стоимость: {price}
    Комментарий: {comment}

    """
    send_mail(
        subject, body, email, ["admin@rockenrolla.net", ],
    )
