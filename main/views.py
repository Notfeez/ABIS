from django.shortcuts import render
from .models import User, Loan, Book

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

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('NonRegister')  # или другая страница после входа
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})