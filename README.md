# Проект Foodgram

[![Actions Status](https://github.com/Vofkabob/foodgram-project-react/workflows/Django-app%20workflow/badge.svg)](https://github.com/Vofkabob/csp-generator/actions)



## Описание проекта:

Добро пожаловать в "Foodgram", сервис, где вы сможете хранить свои рецепты. Помимо этого, в "Foodgram" вы сможете просматривать рецепты других пользователей, добавлять их в избранное или в список покупок, который можно скачать.


## Для установки проекта следуйте инструкциям ниже по порядку

Скопируйте репозиторий:
```
git clone https://github.com/Vofkabob/yamdb_final.git
```

### Действия на сервере

- Зайдите на ваш удалённый сервер и проверьте установку docker:
```
sudo apt install docker.io 
```
- *Если программа не установлена, то произойдёт загрузка. Есть такая программа уже имеется, Вы получите соответствуещее сообщение.

- Скопируйте файлы docker-compose.yml и nginx.conf из директории infra на сервер (либо командой scp либо можете создать файлы на сервере и скопировать туда данные).


### Действия локально

- Отредактируйте файл infra/nginx.conf и в строке server_name впишите свой IP.
- Создайте файл .env в директории infra/ и внестите в него данные:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=django_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD= # установите свой пароль и укажите его в settings.py в default=
DB_HOST=localhost
DB_PORT=5432
```


### Действия в GitHub

- Чтобы workflow работал корректно, добавьте ключи в настройках GitHub - Settings/Secrets/Actions:
```
DOCKER_USERNAME=<имя пользователя DockerHub>
DOCKER_PASSWORD=<пароль от DockerHub>

USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (для его получения команда: cat ~/.ssh/id_rsa)>

TELEGRAM_TO=<ID чата, в который придет сообщение> - его можно узнать у бота @userinfobot
TELEGRAM_TOKEN=<токен вашего бота> - его можно узнать у бота @BotFather
```


### Действия на сервере

- Соберите docker-compose:
```
sudo docker-compose up -d --build
```

- После первого деплоя и сборки выполните команды:

Сбор статики:
```
sudo docker-compose exec backend python manage.py collectstatic --noinput
```

Применение миграций:
```
sudo docker-compose exec backend python manage.py migrate --noinput
```

Создание суперпользователя:
```
sudo docker-compose exec backend python manage.py createsuperuser
```

Проверьте, что запущены 3 контейнера в одном образе: nginx, db, backend. Контейнер frontend будет неактивным, так и должно быть.

Чтобы заполнить базу данных начальными данными списка ингридиетов выполните:
```
sudo docker-compose exec backend python manage.py load_data
```

## Действия в админке:

Обязательно создайте теги "Завтрак", "Обед" и "Ужин" в панели администратора, иначе рецепты не будут добавляться.

## Страниц проекта:

Foodgram будет доступен по ссылке - http://<Ваш_IP>/

Мой Foodgram для примера - http://84.201.178.224/
email: sergeev90@ya.ru
password: password

### Автор:

Сергеев Владимир - https://github.com/Vofkabob
