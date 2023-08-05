# Create your models here.
# library/models.py
from django.db import models

# from django.core.validators import MinValueValidator


# Создадим модель, в которой будем хранить данные о книгах
# class User(models.Model):
#     name = models.CharField(max_length=200)  # Название
#     isbn = models.CharField(max_length=100)  # Индекс издания
#     pages = models.IntegerField(  # Количество страниц
#         validators=[MinValueValidator(1)]
#     )


GENRE_CHOICES = (
    ("R", "Рок"),
    ("E", "Электроника"),
    ("P", "Поп"),
    ("C", "Классика"),
    ("O", "Саундтреки"),
)


class CD(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    artist = models.CharField(max_length=40)
    date = models.DateField()
    genre = models.CharField(max_length=1, choices=GENRE_CHOICES)

    def __repr__(self):
        return "Вот я такой кросавчик"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    body = models.TextField()
    is_answered = models.BooleanField(default=False)
