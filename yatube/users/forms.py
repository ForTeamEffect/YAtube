# library/forms.py
from django import forms
# Импортируем модуль forms, из него возьмём класс ModelForm

from .models import Contact  # Импортируем модель, чтобы связать с ней форму

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


#  создадим собственный класс для формы регистрации
#  сделаем его наследником предустановленного класса UserCreationForm
class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # укажем модель, с которой связана создаваемая форма
        model = User
        # укажем, какие поля должны быть видны в форме и в каком порядке
        fields = ('first_name', 'last_name', 'username', 'email')


# class CreationForm(forms.ModelForm.UserCreationForm):
#     class Meta:
#         # Эта форма будет работать с моделью Book
#         model = User
#
#         # Здесь перечислим поля модели, которые должны
#         отображаться в веб-форме;
#         # при необходимости можно вывести в веб-форму
#         только часть полей из модели.
#         fields = ('name', 'isbn', 'pages')


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'email', 'subject', 'body')

    # Метод-валидатор для поля subject
    def clean_subject(self):
        data = self.cleaned_data['subject']

        # Если пользователь не поблагодарил
        # администратора - считаем это ошибкой
        if 'спасибо' not in data.lower():
            raise forms.ValidationError(
                'Вы обязательно должны нас поблагодарить!')

        # Метод-валидатор обязательно должен вернуть очищенные данные,
        # даже если не изменил их
        return data

# class ExchangeForm(forms.Form):
#     name = forms.CharField(max_length=100)
#     email = forms.EmailField()
#     title = forms.CharField(max_length=100)
#     artist = forms.CharField(max_length=40)
#     genre = forms.ChoiceField(choices=GENRE_CHOICES)
#     price = forms.DecimalField(required=False)
#     comment = forms.Textarea(required=False)
#     forms.CharField(label="comment", widget=forms.Textarea)
# from django.forms import ModelForm
# #####################################
# class BaseForm(ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(BaseForm, self).__init__(*args, **kwargs)
#         for bound_field in self:
#             if hasattr(bound_field, "field") and bound_field.field.required:
#                 bound_field.field.widget.attrs["required"] = "required"
# # А затем пусть все объекты формы спускаются от него:
#
# class UserForm(BaseForm):
#     class Meta:
#         model = User
#         fields = []
#
#     first_name = forms.CharField(required=True)
#     last_name = forms.CharField(required=True)
#     email = forms.EmailField(required=True, max_length=100)
