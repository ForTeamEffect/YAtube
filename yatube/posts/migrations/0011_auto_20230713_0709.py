# Generated by Django 2.2.16 on 2023-07-13 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20230712_0847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Загрузите картинку', upload_to='posts/', verbose_name='Картинка'),
        ),
    ]
