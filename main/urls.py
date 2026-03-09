from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('change-email/', views.change_email, name='change_email'),
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html',success_url='/password-change-done/'), name='password_change'),
    path('password-change-done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    
    # Reader 
    path('reader/request_book/<uuid:book_id>/', views.request_book, name='request_book'),
    path('reader/cancel_request/<uuid:request_id>/', views.cancel_request, name='cancel_request'),
    path('reader/profile/', views.reader_profile, name='reader_profile'),
    path('reader/book/<uuid:book_id>/', views.book_detail, name='book_detail'),
    path('reader/my_books/', views.my_books_list, name='my_books'),
    
    # Librarian 
    path('librarian/requests/', views.librarian_requests, name='librarian_requests'),
    path('librarian/approve/<uuid:request_id>/', views.approve_request, name='approve_request'),
    path('librarian/reject/<uuid:request_id>/', views.reject_request, name='reject_request'),
    path('librarian/return/<uuid:loan_id>/', views.return_book, name='return_book'),

    path('export/books/csv/', views.export_books_csv, name='export_books_csv'),
]