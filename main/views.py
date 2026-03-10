from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Loan, Book, Request
from django.contrib.auth import authenticate, login
from .forms import CustomUserCreationForm, EmailAuthenticationForm
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.http import HttpResponse
import csv
from datetime import datetime

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
    if request.user.role == User.Roles.ADMIN:
        return admin_panel(request)
    elif request.user.role == User.Roles.LIBRARIAN:
        return librarian(request)
    else:  
        return Chitatel(request)
    
@login_required
def Chitatel(request):
    total_books = Book.objects.count()
    available_books = Book.objects.filter(status='available').count()
    on_loan_books = Book.objects.filter(status='on_loan').count()
    all_books = Book.objects.all()
    my_books = Loan.objects.filter(reader=request.user, return_date__isnull=True).select_related('book')
    my_requests = Request.objects.filter(reader=request.user).order_by('-request_date')  # добавить

    active_tab = request.GET.get('tab', 'catalog')
    return render(request, 'Chitatel.html', {
        'total_books': total_books,
        'available_books': available_books,
        'on_loan_books': on_loan_books,
        'all_books': all_books,
        'my_books': my_books,
        'my_requests': my_requests,
        'active_tab': active_tab,
    })

@login_required
def request_book(request, book_id):
    if request.user.role != User.Roles.READER:
        messages.error(request, 'Только читатели могут запрашивать книги.')
        return redirect('dashboard')

    book = get_object_or_404(Book, book_id=book_id)

    if Request.objects.filter(reader=request.user, book=book, status='pending').exists():
        messages.error(request, 'Вы уже отправили запрос на эту книгу.')
        return redirect('dashboard')

    if book.status != 'available':
        messages.error(request, f'Книга "{book.title}" сейчас недоступна.')
        return redirect('dashboard')

    # Создаём запрос
    Request.objects.create(reader=request.user, book=book)
    messages.success(request, f'Запрос на книгу "{book.title}" отправлен. Ожидайте подтверждения библиотекаря.')
    return redirect('dashboard')
        
@login_required
def librarian(request):
    if request.user.role != User.Roles.LIBRARIAN:
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')

    total_books = Book.objects.count()
    total_readers = User.objects.filter(role=User.Roles.READER).count()
    total_loans = Loan.objects.count()

    pending_requests = Request.objects.filter(status='pending').select_related('reader', 'book')

    active_loans = Loan.objects.filter(return_date__isnull=True).select_related('reader', 'book')

    query = request.GET.get('q', '')
    books = Book.objects.all().order_by('title')
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query)
        )
    available_books = books.filter(status='available').count()
    on_loan_books = books.filter(status='on_loan').count()
    total_books_catalog = books.count()

    context = {
        'total_books': total_books,
        'total_readers': total_readers,
        'total_loans': total_loans,
        'pending_requests': pending_requests,
        'active_loans': active_loans,
        'books': books,
        'query': query,
        'available_books': available_books,
        'on_loan_books': on_loan_books,
        'total_books_catalog': total_books_catalog,
    }
    return render(request, 'librarian.html', context)

@login_required
def librarian_requests(request):
    if request.user.role != User.Roles.LIBRARIAN:
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')
    requests_list = Request.objects.filter(status='pending').select_related('reader', 'book')
    return render(request, 'librarian_requests.html', {'requests': requests_list})

@login_required
def approve_request(request, request_id):
    if request.user.role != User.Roles.LIBRARIAN:
        return redirect('dashboard')
    
    book_request = get_object_or_404(Request, request_id=request_id, status='pending')
    
    # Get days from POST or use default 14
    days = int(request.POST.get('days', 14)) if request.method == 'POST' else 14
    
    due_date = timezone.now().date() + timedelta(days=days)
    Loan.objects.create(
        reader=book_request.reader,
        book=book_request.book,
        due_date=due_date
    )
    book_request.status = 'approved'
    book_request.save()
    messages.success(request, f'Запрос на книгу "{book_request.book.title}" одобрен на {days} дней.')
    return redirect('dashboard')

@login_required
def reject_request(request, request_id):
    if request.user.role != User.Roles.LIBRARIAN:
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')
    book_request = get_object_or_404(Request, request_id=request_id, status='pending')
    if request.method == 'POST':
        comment = request.POST.get('comment', '')
        book_request.status = 'rejected'
        book_request.librarian_comment = comment
        book_request.save()
        messages.success(request, f'Запрос на книгу "{book_request.book.title}" отклонён.')
        return redirect('librarian_requests')
    return redirect('dashboard')

@login_required
def return_book(request, loan_id):
    if request.user.role != User.Roles.LIBRARIAN:
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')
    
    loan = get_object_or_404(Loan, loan_id=loan_id)
    loan.return_book()
    messages.success(request, f'Книга "{loan.book.title}" отмечена как возвращённая.')
    return redirect('dashboard')

@login_required
def cancel_request(request, request_id):
    """Читатель отменяет свой запрос на книгу"""
    if request.user.role != User.Roles.READER:
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')
    
    book_request = get_object_or_404(Request, request_id=request_id, reader=request.user)
    
    if book_request.status != 'pending':
        messages.error(request, 'Можно отменить только ожидающий запрос.')
        return redirect('dashboard')
    
    book_title = book_request.book.title
    book_request.delete()
    messages.success(request, f'Запрос на книгу "{book_title}" отменён.')
    return redirect('dashboard?tab=my_requests')

@login_required
def reader_profile(request):
    """Профиль и настройки читателя"""
    if request.user.role != User.Roles.READER:
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        
        request.user.first_name = first_name
        request.user.last_name = last_name
        if hasattr(request.user, 'phone'):
            request.user.phone = phone
        request.user.save()
        
        messages.success(request, 'Профиль успешно обновлён.')
        return redirect('dashboard?tab=settings')
    
    return render(request, 'Chitatel.html', {
        'active_tab': 'settings',
        'total_books': Book.objects.count(),
        'available_books': Book.objects.filter(status='available').count(),
        'on_loan_books': Book.objects.filter(status='on_loan').count(),
    })

@login_required
def book_detail(request, book_id):
    """Детальный просмотр книги"""
    book = get_object_or_404(Book, book_id=book_id)
    reader_loan = None
    reader_request = None
    
    if request.user.is_authenticated and request.user.role == User.Roles.READER:
        # Check if reader has this book
        reader_loan = Loan.objects.filter(
            reader=request.user, 
            book=book, 
            return_date__isnull=True
        ).first()
        # Check if reader has pending request
        reader_request = Request.objects.filter(
            reader=request.user,
            book=book,
            status='pending'
        ).first()
    
    context = {
        'book': book,
        'reader_loan': reader_loan,
        'reader_request': reader_request,
    }
    return render(request, 'book_detail.html', context)

@login_required
def my_books_list(request):
    """Список книг читателя"""
    if request.user.role != User.Roles.READER:
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')
    
    my_books = Loan.objects.filter(
        reader=request.user, 
        return_date__isnull=True
    ).select_related('book').order_by('due_date')
    
    context = {
        'my_books': my_books,
        'total_books': Book.objects.count(),
        'available_books': Book.objects.filter(status='available').count(),
        'on_loan_books': Book.objects.filter(status='on_loan').count(),
    }
    return render(request, 'Chitatel.html', context)


# ============================================================================
# ADMIN FUNCTIONS
# ============================================================================

@login_required
def admin_panel(request):
    """Главная панель администратора"""
    if request.user.role != User.Roles.ADMIN:
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')
    
    active_tab = request.GET.get('tab', 'overview')
    
    # Statistics
    total_books = Book.objects.count()
    total_users = User.objects.filter(role=User.Roles.READER).count()
    total_librarians = User.objects.filter(role=User.Roles.LIBRARIAN).count()
    total_loans = Loan.objects.count()
    overdue_loans = Loan.get_overdue_loans().count()
    
    # Data for tabs
    all_books = Book.objects.all().order_by('title')
    all_readers = User.objects.filter(role=User.Roles.READER).all().order_by('email')
    all_librarians = User.objects.filter(role=User.Roles.LIBRARIAN).all().order_by('email')
    
    context = {
        'active_tab': active_tab,
        'total_books': total_books,
        'total_users': total_users,
        'total_librarians': total_librarians,
        'total_loans': total_loans,
        'overdue_loans': overdue_loans,
        'all_books': all_books,
        'all_readers': all_readers,
        'all_librarians': all_librarians,
    }
    
    return render(request, 'admin.html', context)

@login_required
def export_books_csv(request):
    """Экспорт каталога книг в CSV"""
    if request.user.role != User.Roles.ADMIN:
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="books_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    # Add BOM for proper UTF-8 encoding in Excel
    response.write('\ufeff')
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Название', 'Автор', 'ISBN', 'Статус', 'Дата публикации'])
    
    books = Book.objects.all().order_by('title')
    for book in books:
        writer.writerow([
            str(book.book_id),
            book.title,
            book.author,
            book.isbn or '—',
            book.get_status_display(),
            book.publication_date or '—',
        ])
    
    return response

@login_required
def export_users_csv(request):
    """Экспорт пользователей в CSV"""
    if request.user.role != User.Roles.ADMIN:
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    # Add BOM for proper UTF-8 encoding in Excel
    response.write('\ufeff')
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Email', 'Имя', 'Фамилия', 'Роль', 'Дата регистрации'])
    
    users = User.objects.all().order_by('email')
    for user in users:
        writer.writerow([
            str(user.id),
            user.email,
            user.first_name or '—',
            user.last_name or '—',
            user.get_role_display(),
            user.date_joined.strftime("%d.%m.%Y %H:%M"),
        ])
    
    return response

@login_required
def make_librarian(request, user_id):
    """Назначить пользователя библиотекарем"""
    if request.user.role != User.Roles.ADMIN:
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if user.role == User.Roles.ADMIN:
        messages.error(request, 'Невозможно изменить роль администратора.')
        return redirect('dashboard?tab=users')
    
    if user.role == User.Roles.LIBRARIAN:
        messages.warning(request, f'{user.email} уже является библиотекарем.')
        return redirect('dashboard?tab=users')
    
    user.role = User.Roles.LIBRARIAN
    user.save()
    messages.success(request, f'{user.email} назначен(а) библиотекарем.')
    return redirect('dashboard?tab=users')

@login_required
def remove_librarian(request, user_id):
    """Снять пользователя с должности библиотекаря"""
    if request.user.role != User.Roles.ADMIN:
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if user.role == User.Roles.LIBRARIAN:
        user.role = User.Roles.READER
        user.save()
        messages.success(request, f'{user.email} больше не является библиотекарем.')
    else:
        messages.warning(request, f'{user.email} не является библиотекарем.')
    
    return redirect('dashboard?tab=users')

@login_required
def change_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('new_email')
        if User.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
            messages.error(request, 'Этот email уже используется другим пользователем.')
        else:
            request.user.email = new_email
            request.user.save()
            messages.success(request, 'Email успешно изменён.')
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def reader_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        messages.success(request, 'Профиль обновлён.')
    return redirect('dashboard')

@login_required
@user_passes_test(lambda u: u.role == 'librarian') # ВРЕМЕННОЕ РЕШЕНИЕ, ПОКА НЕ РЕАЛИЗОВАНО ПОЛНОСТЬЮ РАЗГРАНИЧЕНИЕ РОЛЕЙ
def export_books_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="books_catalog.csv"'

    response.write('\ufeff'.encode('utf-8'))

    writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(['ID', 'Название', 'Автор', 'ISBN', 'Статус', 'Дата публикации'])
    books = Book.objects.all()
    for book in books:
        writer.writerow([
            book.book_id,
            book.title,
            book.author,
            book.isbn or '',
            book.get_status_display(),
            book.publication_date.strftime('%d.%m.%Y') if book.publication_date else ''
        ])

    return response

@login_required
@user_passes_test(lambda u: u.role == 'librarian')
def return_book(request, loan_id):
    loan = get_object_or_404(Loan, loan_id=loan_id, return_date__isnull=True)
    if request.method == 'POST':
        loan.return_book()
        messages.success(request, f'Книга "{loan.book.title}" успешно возвращена.')
    else:
        messages.error(request, 'Неверный метод запроса.')

    return redirect('dashboard')