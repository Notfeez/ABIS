from django.contrib import admin

from .models import Client, Librarian

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'last_name', 'email', 'role')

@admin.register(Librarian)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'last_name', 'email', 'role')