import os
import sys
from django.core.files import File
from datetime import date

# Настройка Django для запуска вне manage.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')
import django
django.setup()

from main.models import Book

titles = [
    "1984",
    "Белая гвардия",
    "Великий Гэтсби",
    "Вино из одуванчиков",
    "Война и мир",
    "Герой нашего времени",
    "Град обреченный",
    "Дар",
    "Доктор Живаго",
    "Дюна",
    "Золотой теленок",
    "Игра в бисер",
    "Камера обскура",
    "Король, дама, валет",
    "Лолита",
    "Марсианские хроники",
    "Мастер и Маргарита",
    "Над пропастью во ржи",
    "Осень патриарха",
    "Отцы и дети",
    "Отчаяние",
    "Подвиг",
    "Приглашение на казнь",
    "Скотный двор",
    "Собачье сердце",
    "Сто лет одиночества",
    "Триумфальная арка",
    "Трудно быть богом",
    "Улитка на склоне",
    "Хроники Амбера",
    "Шантарам",
]

COVERS_DIR = os.path.join('media', 'book_covers')

books_created = 0
books_with_cover = 0

for title in titles:
    if Book.objects.filter(title=title).exists():
        print(f"Книга '{title}' уже существует. Пропускаем.")
        continue

    book = Book(
        title=title,
        author="Неизвестный автор",  # можно заменить позже
        publication_date=date(2000, 1, 1),
        status='available'
    )
    book.save()
    books_created += 1

    cover_found = False
    for ext in ['.jpg', '.jpeg', '.png', '.gif']:
        filename = f"{title}{ext}"
        full_path = os.path.join(COVERS_DIR, filename)
        if os.path.exists(full_path):
            with open(full_path, 'rb') as f:
                book.image.save(filename, File(f), save=True)
            print(f"Обложка добавлена для '{title}'")
            books_with_cover += 1
            cover_found = True
            break
    if not cover_found:
        print(f"Обложка для '{title}' не найдена")

print(f"\nСоздано книг: {books_created}")
print(f"Привязано обложек: {books_with_cover}")