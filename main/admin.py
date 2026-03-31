from django.contrib import admin
from .models import User, Book, Loan

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'status', 'get_image_preview')
    list_filter = ('status', 'publication_date')
    search_fields = ('title', 'author', 'isbn')
    fields = ('title', 'author', 'isbn', 'publication_date', 'status', 'image', 'get_image_preview')
    readonly_fields = ('get_image_preview',)
    
    def get_image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="150" style="object-fit:cover;border-radius:4px;" />'
        return "Нет обложки"
    get_image_preview.short_description = "Предпросмотр обложки"
    get_image_preview.allow_tags = True

admin.site.register(User)
admin.site.register(Book, BookAdmin)
admin.site.register(Loan)