from django.db import models

# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    email = models.EmailField(unique=True, verbose_name="Email")
    password = models.CharField(max_length=128, verbose_name="Пароль") 
    role = models.BooleanField(default=False, verbose_name="Права")  # False = обычный пользователь, True = админ

    def __str__(self):
        return f"{self.name} {self.last_name}"
    
class Librarian(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    email = models.EmailField(unique=True, verbose_name="Email")
    password = models.CharField(max_length=128, verbose_name="Пароль") 
    role = models.BooleanField(default=True, verbose_name="Права")  # False = обычный пользователь, True = админ

    def __str__(self):
        return f"{self.name} {self.last_name}"