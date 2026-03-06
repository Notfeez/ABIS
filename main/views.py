from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Loan, Book
from django.contrib.auth import authenticate, login
from .forms import CustomUserCreationForm, EmailAuthenticationForm
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

# Create your views here.

def index(request):
    total_books = Book.objects.count()
    available_books = Book.objects.filter(status='available').count()
    on_loan_books = Book.objects.filter(status='on_loan').count()
    all_books = Book.objects.all()
    books = Book.objects.all()
    from django.db.models import Q
    
    query = request.GET.get('q', '')
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query)
        )

    return render(request, 'NotRegister.html', {
        'total_books': total_books,
        'available_books': available_books,
        'on_loan_books': on_loan_books,
        'all_books' : books,
        'query': query,
    })

def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user) 
            return redirect('dashboard')
        else:
            print(form.errors)
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            backend = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user, backend=backend)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
#    if request.user.role == User.Roles.ADMIN:
#        return render(request, 'admin_dashboard.html')
    if request.user.role == User.Roles.LIBRARIAN:
        return render(request, 'librarian.html')
    else:  
        return Chitatel(request)
    
@login_required
def Chitatel(request):
    total_books = Book.objects.count()
    available_books = Book.objects.filter(status='available').count()
    on_loan_books = Book.objects.filter(status='on_loan').count()
    all_books = Book.objects.all()
    my_books = Loan.objects.filter(reader=request.user, return_date__isnull=True).select_related('book')
  
    
    active_tab = request.GET.get('tab', 'catalog')
    return render(request, 'Chitatel.html', {
        'total_books': total_books,
        'available_books': available_books,
        'on_loan_books': on_loan_books,
        'all_books': all_books,
        'my_books': my_books,
        'active_tab': active_tab,
    })


def request_book(request, book_id):
    if request.user.role != User.Roles.READER:
        book = get_object_or_404(Book, book_id=book_id)

        if book.status == 'available':
            existing_loan = Loan.objects.filter(
                reader=request.user,
                book=book,
                return_date__isnull=True
            ).exists()
            if existing_loan:
                messages.error(request, 'Вы уже запросили эту книгу.')
                return redirect('Chitatel')

            due_date = timezone.now().date() + timedelta(days=14)

            loan = Loan.objects.create(
                reader=request.user,
                book=book,
                due_date=due_date
            )

            messages.success(
                request,
                f'Книга "{book.title}" успешно запрошена. Срок возврата: {due_date.strftime("%d.%m.%Y")}'
            )
        else:
            messages.error(request, f'Книга "{book.title}" сейчас недоступна.')

        return redirect('Chitatel')
        
        #temporary
@login_required
def librarian(request):
    return render(request, 'librarian.html')
        
        #temporary
def administrator(request):
    return render(request, 'admin.html')