### Как запустить проект:


то что вам нужно лежит в:
yatube/templates/menu.html
yatube/core/templatetags/menu_tags.py
yatube/menu/models.py

писал на Python 3.9.11


Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/ForTeamEffect/YAtube.git
```

```
cd yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

