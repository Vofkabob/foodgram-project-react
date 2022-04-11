*тут будет бейдж workflow!*

### Проект Foodgram

## Описание проекта:

Добро пожаловать в "Foodgram", сервис, где вы сможете хранить свои рецепты. Помимо этого, в "Foodgram" вы сможете просматривать рецепты других пользователей, добавлять их в избранное или в список покупок, который можно скачать.

## Для установки проекта (инструкция для Windows):

Скопируйте репозиторий
```
git clone https://github.com/Vofkabob/yamdb_final.git
```

Создайте и разверните виртуальное окружение, установите зависимости
```
python -m venv venv или python3 -m venv venv
source venv/Scripts/activate
pip install requirements.txt
```

Создайте файл .env в директории infra/ и внестите в него данные
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=django_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD= # установите свой пароль и укажите его в settings.py в default=
DB_HOST=localhost
DB_PORT=5432
```

Соберите статику
```
python manage.py collectstatic
```

Запустите docker-compose
```
docker-compose up --build
```

Проверьте, что запущены 3 контейнера в одном образе: nginx, db, frontend. Контейнер frontend будет неактивным, так и должно быть.

Далее перейдите в директорию с файлом manage.py (foodgram-project-react\backend\foodgram_project)

Запустите проект
```
python manage.py runserver
```

*К описанию добавятся настройки удалённого сервера после первого ревью*

## Страниц проекта:

Foodgram будет доступен по ссылке - http://localhost/recipes

## Автор:

Сергеев Владимир - https://github.com/Vofkabob
