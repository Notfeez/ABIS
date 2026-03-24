Запуск: python manage.py runserver
БД: python manage.py makemigrations
    python manage.py migrate

Создание книг: python create_books.py
// ds
Создать виртуальное окружение и установить зависимости (pip install -r requirements.txt).

Создать базу данных в PostgreSQL (шаг 2) с теми же именем и пользователем (или изменить параметры в .env).

Создать файл .env на основе примера (можно добавить .env.example в репозиторий).

Применить миграции: python manage.py migrate.

При необходимости загрузить фикстуры: python manage.py loaddata initial_data