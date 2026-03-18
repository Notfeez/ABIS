from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    
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
    path('return/<uuid:loan_id>/', views.return_book, name='return_book'),

    path('export/books/csv/', views.export_books_csv, name='export_books_csv'),

    #admnin
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/export/loans/', views.export_loans_csv, name='export_loans_csv'),
    path('admin/export/books/', views.export_books_csv, name='export_books_csv'),
    path('admin/export/users/', views.export_users_csv, name='export_users_csv'),
    path('admin/users/', views.user_list, name='user_list'),
    path('admin/add-book/', views.add_book, name='add_book'),
    path('admin/toggle-librarian/<uuid:user_id>/', views.toggle_librarian, name='toggle_librarian'),
    path('admin/2fa/', views.admin_2fa, name='admin_2fa'),
    path('admin/change-password/', views.admin_change_password, name='admin_change_password'),
    path('admin/change-email/', views.admin_change_email, name='admin_change_email'),
    
    #resets (pass+email)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url='/password-reset-done/'
         ),
         name='password_reset'),

    path('password-reset-done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ),
         name='password_reset_confirm'),

    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    path('change-email/', views.change_email_page, name='change_email_page'),
    
    # Обработка формы (POST)
    path('change-email/submit/', views.change_email, name='change_email'),
    path('admin/delete-book/<uuid:book_id>/', views.delete_book, name='delete_book'),
]