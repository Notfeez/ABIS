from time import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.

class Reader(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=False, blank=False, help_text="Имя читателя", verbose_name="Имя")
    last_name = models.CharField(max_length=100, null=False, blank=False, help_text="Фамилия читателя", verbose_name="Фамилия")
    email = models.EmailField(unique=True, max_length=254, verbose_name="Email", help_text="Email адрес (будет сохранен в нижнем регистре)")
    
    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        if not self.name or not self.last_name:
            raise ValueError("Имя и фамилия обязательны")
        super().save(*args, **kwargs)

class Book(models.Model):
    book_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID книги")
    title = models.CharField(max_length=200, verbose_name="Название")
    author = models.CharField(max_length=100, verbose_name="Автор")
    publication_date = models.DateField(null=True, blank=True, verbose_name="Дата публикации")
    
    LOAN_STATUS = [
        ('available', 'Доступна'),
        ('on_loan', 'В аренде'),
        ('reserved', 'Зарезервирована'),
    ]
    
    status = models.CharField(max_length=20, choices=LOAN_STATUS, default='available', verbose_name="Статус")
    isbn = models.CharField(max_length=13, unique=True, null=True, blank=True, verbose_name="ISBN")
    
    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['title', 'author']
    
    def __str__(self):
        return f"{self.title} - {self.author}"
    
    def is_available(self):
        return self.status == 'available'

class Loan(models.Model):
    loan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID Запроса")
    reader = models.ForeignKey(Reader, on_delete=models.PROTECT, related_name='loans', verbose_name="Читатель")
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='loans', verbose_name="Книга")
    borrow_date = models.DateField(auto_now_add=True, verbose_name="Дата выдачи")
    due_date = models.DateField(verbose_name="Срок возврата")
    return_date = models.DateField(null=True, blank=True, verbose_name="Фактическая дата возврата")
    
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('returned', 'Возвращен'), 
        ('overdue', 'Просрочен'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    
    class Meta:
        verbose_name = "Аренда"
        verbose_name_plural = "Аренды"
        ordering = ['-borrow_date']
        indexes = [models.Index(fields=['status', 'due_date'])]
    
    def __str__(self):
        return f"{self.book.title} - {self.reader.last_name} {self.reader.name}"
    
    def save(self, *args, **kwargs):
        if self.return_date:
            self.status = 'returned'
        elif self.due_date and self.due_date < timezone.now().date():
            self.status = 'overdue'
        else:
            self.status = 'active'
        
        if not self.pk:
            if self.book.status != 'available':
                raise ValueError(f"Книга '{self.book.title}' недоступна для аренды")
            self.book.status = 'on_loan'
            self.book.save()
        
        super().save(*args, **kwargs)
    
    def is_overdue(self):
        if self.return_date:
            return False
        return self.due_date < timezone.now().date()
    
    def days_overdue(self):
        if not self.is_overdue():
            return 0
        return (timezone.now().date() - self.due_date).days
    
    def return_book(self):
        self.return_date = timezone.now().date()
        self.status = 'returned'
        self.book.status = 'available'
        self.book.save()
        self.save()
    
    @classmethod
    def get_overdue_loans(cls):
        return cls.objects.filter(return_date__isnull=True, due_date__lt=timezone.now().date())
    
class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        LIBRARIAN = 'librarian', 'Библиотекарь'
        READER = 'reader', 'Читатель'
    
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.READER, verbose_name="Роль")
    
    reader_profile = models.OneToOneField('Reader', on_delete=models.SET_NULL, null=True, blank=True, related_name='user')
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
    
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
    
    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN
    
    @property
    def is_librarian(self):
        return self.role == self.Roles.LIBRARIAN
    
    @property
    def is_reader(self):
        return self.role == self.Roles.READER