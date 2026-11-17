# BlueLine — информационная система салона связи

Курсовая работа: **«Разработка информационной системы салона связи»**.

Учебный проект на **Python + Django** для ИП **BlueLine** — салона связи, который занимается ресейлом техники Apple (новые и восстановленные устройства, trade-in, услуги настройки и связи).

## Что умеет система

- витрина каталога с фильтром по категориям и покупкой;
- журнал заказов и складской учёт остатков;
- услуги салона и заявки клиентов;
- аналитика продаж (выручка, средний чек, mix по линейкам);
- админ-панель **django-jazzmin** для CRUD по всем сущностям.

Стек: Django 5.2, SQLite (`db.sqlite3`), Jazzmin.

## Запуск локально

```bash
.\.venv315\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Открыть: `http://127.0.0.1:8000/`  
Админка: `http://127.0.0.1:8000/admin/`

Демо-вход в админку: `admin` / `admin123`. На боевом хостинге пароль нужно сменить.

## Структура

- `info_flow/` / `info_site/` — настройки проекта, URL, WSGI;
- `salon/` — модели, представления, админка, демо-данные;
- `templates/` — публичные страницы и кастомная главная Jazzmin;
- `static/css/` — синяя тема сайта и админки.

## PythonAnywhere

Новый сайт поднимается в том же Web-приложении, что и старый. Новый аккаунт создавать не нужно.

Рабочая папка на сервере — каталог, где лежит `manage.py` (локально это `info_flow`). Модуль настроек: `info_flow.settings`. База — файл `db.sqlite3` рядом с `manage.py`.

1. Загрузить обновлённые файлы (Git pull или Files). Папки `.venv` и `.venv315` не копировать.
2. В Bash открыть каталог проекта и виртуальное окружение сайта. Если окружение старше Python 3.10, создать новое: Django 5.2 на Python 3.9 не ставится. В Web → Virtualenv указать путь к этому окружению.
3. `pip install -r requirements.txt`
4. `python manage.py migrate`
5. `python manage.py seed_demo` — если нужна демо-витрина. Команда обновляет демо-товары и не удаляет суперпользователя.
6. `python manage.py collectstatic --noinput`
7. В Web → Static files: URL `/static/` → папка `staticfiles` внутри проекта.
8. В файле WSGI (Web → WSGI configuration file) путь в `sys.path` должен указывать на каталог с `manage.py`, а настройки — на `info_flow.settings`. Туда же добавить доверенный origin:

```python
import os
import sys

path = "/home/ВАШ_ЛОГИН/info_flow"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "info_flow.settings"
os.environ["CSRF_TRUSTED_ORIGINS"] = "https://ВАШ_ЛОГИН.pythonanywhere.com"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

`ALLOWED_HOSTS` уже принимает любой хост `*.pythonanywhere.com`.

9. На вкладке Web нажать зелёную кнопку **Reload**.
10. Если страница не открывается — Error log на той же вкладке. Частые причины: неверный путь в WSGI, не установлен Jazzmin, не выполнен `collectstatic`, у `db.sqlite3` нет прав на запись.
