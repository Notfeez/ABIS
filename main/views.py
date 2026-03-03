from django.shortcuts import render, redirect
from .models import User, Loan, Book
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from .forms import CustomUserCreationForm, EmailAuthenticationForm
from django.conf import settings
# Create your views here.

def index(request):
    total_books = Book.objects.count()
    available_books = Book.objects.filter(status='available').count()
    on_loan_books = Book.objects.filter(status='on_loan').count()
    all_books = Book.objects.all()

    return render(request, 'NotRegister.html', {
        'total_books': total_books,
        'available_books': available_books,
        'on_loan_books': on_loan_books,
        'all_books' : all_books,
    })

def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('NonRegister')  # замените на нужный маршрут
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            backend = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user)  # автоматический вход после регистрации
            return redirect('index')  # замените на имя вашего главного маршрута
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})