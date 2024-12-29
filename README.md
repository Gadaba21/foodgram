#  Проэкт Фудграм

## О проэкте

Делитесь рецептами, подписывайтесь, скачивайте и готовте


## Что можно делать на сайт

- Выкладывать рецепты.
- Добавлять в избранное рецепты
- Подписываться на других авторов
- Распечатать список покупок

## Примеры запросов к api

http://127.0.0.1:9999/api/recipes/
http://127.0.0.1:9999/api/user/me


## Список использованных библиотек

Django==3.2.15
django-colorfield==0.7.2
django-debug-toolbar==3.2.4
django-filter==22.1
djangorestframework==3.14.0
djangorestframework-simplejwt==4.8.0
djoser==2.1.0
drf-extra-fields==3.4.0
gunicorn==20.1.0
psycopg2-binary==2.9.3
PyJWT==2.5.0
python-dotenv==0.21.0
pytz==2022.2.1
reportlab==3.6.11
requests==2.28.1
sqlparse==0.4.3
environs==9.5.0
django-cors-headers==3.13.0


## Чтобы запустить проэкт наобходимо 

Развернуть виртуальное окружение и активировать его
python -m venv venv
source venv/Scripts/activate
Обновить PIP
python -m pip install --upgrade pip
Установить зависимости из файла requirements.txt:
pip install -r requirements.txt
Установить миграции
python manage.py makemigrations
python manage.py migrate
запуск сервера
python manage.py runserver




