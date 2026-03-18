from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import User, Loan, Book, Request
from django.contrib.auth import authenticate, login, update_session_auth_hash
from .forms import CustomUserCreationForm, EmailAuthenticationForm, BookForm 
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
import csv
from django.core.paginator import Paginator
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import views as auth_views
from django.core.mail import send_mail
from django.template.loader import render_to_string
import random

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
            # if user.role == User.Roles.ADMIN:
            #     code = generate_2fa_code()
            #     request.session['pre_auth_user_id'] = str(user.id)
            #     request.session['2fa_code'] = code
            #     request.session['2fa_code_expiry'] = (timezone.now() + timedelta(minutes=5)).timestamp()
                
            #     send_2fa_code(user.email, code)
                
            #     return redirect('admin_2fa')
            # else:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Неверный email или пароль')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def admin_2fa(request):
    user_id = request.session.get('pre_auth_user_id')
    code = request.session.get('2fa_code')
    expiry = request.session.get('2fa_code_expiry')

    if not user_id or not code or not expiry:
        messages.error(request, 'Несанкционированный доступ')
        return redirect('login')

    if timezone.now().timestamp() > expiry:
        messages.error(request, 'Код истёк. Запросите новый.')
        del request.session['pre_auth_user_id']
        del request.session['2fa_code']
        del request.session['2fa_code_expiry']
        return redirect('login')

    if request.method == 'POST':
        entered_code = request.POST.get('code')
        if entered_code == code:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            login(request, user)
            del request.session['pre_auth_user_id']
            del request.session['2fa_code']
            del request.session['2fa_code_expiry']
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Неверный код')

    return render(request, 'admin_2fa.html')

def admin_required(view_func):
    decorated_view_func = user_passes_test(
        lambda u: u.is_authenticated and u.role == User.Roles.ADMIN,
        login_url='login'
    )(view_func)
    return decorated_view_func

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
        return redirect('admin_dashboard')
    elif request.user.role == User.Roles.LIBRARIAN:
        return librarian(request)
    else:  
        return Chitatel(request)
    
@admin_required
def admin_dashboard(request):
    books = Book.objects.all().order_by('title')
    
    total_books = books.count()
    total_users = User.objects.count()
    total_loans = Loan.objects.count()
    active_loans = Loan.objects.filter(return_date__isnull=True).count()
    
    users_list = User.objects.all().order_by('email')
    paginator = Paginator(users_list, 20)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    active_tab = request.GET.get('tab', 'users')
    
    context = {
        'books': books,            
        'users': users,               
        'total_books': total_books,
        'total_users': total_users,
        'total_loans': total_loans,
        'active_loans': active_loans,
        'active_tab': active_tab,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
@admin_required
def export_loans_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="loans.csv"'
    response.write('\ufeff'.encode('utf-8'))

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ID выдачи', 'Книга', 'Читатель', 'Дата выдачи', 'Срок возврата', 'Дата возврата', 'Статус'])

    loans = Loan.objects.all().select_related('book', 'reader')
    for loan in loans:
        writer.writerow([
            loan.loan_id,
            loan.book.title,
            loan.reader.email,
            loan.borrow_date.strftime('%d.%m.%Y') if loan.borrow_date else '',
            loan.due_date.strftime('%d.%m.%Y') if loan.due_date else '',
            loan.return_date.strftime('%d.%m.%Y') if loan.return_date else '',
            loan.get_status_display()
        ])
    return response

@admin_required
def export_books_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="books.csv"'
    response.write('\ufeff'.encode('utf-8'))

    writer = csv.writer(response, delimiter=';')
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

@admin_required
def export_users_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    response.write('\ufeff'.encode('utf-8'))

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ID', 'Email', 'Имя', 'Фамилия', 'Роль', 'Дата регистрации'])

    users = User.objects.all()
    for user in users:
        writer.writerow([
            user.id,
            user.email,
            user.first_name,
            user.last_name,
            user.get_role_display(),
            user.date_joined.strftime('%d.%m.%Y %H:%M')
        ])
    return response

@admin_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Книга успешно добавлена')
            return redirect('admin_dashboard')
    else:
        form = BookForm()
    return render(request, 'add_book.html', {'form': form})

@admin_required
def user_list(request):
    users_list = User.objects.all().order_by('email')
    paginator = Paginator(users_list, 100)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    active_tab = request.GET.get('tab', 'users')
    
    return render(request, 'admin.html', {
        'users': users,
        'total_users': User.objects.count(),
        'total_books': Book.objects.count(),
        'total_loans': Loan.objects.count(),
        'active_loans': Loan.objects.filter(return_date__isnull=True).count(),
        'active_tab': active_tab,
    })

@admin_required
@require_POST
def toggle_librarian(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.role == User.Roles.LIBRARIAN:
        user.role = User.Roles.READER
        messages.success(request, f'Пользователь {user.email} больше не библиотекарь')
    elif user.role == User.Roles.READER:
        user.role = User.Roles.LIBRARIAN
        messages.success(request, f'Пользователь {user.email} назначен библиотекарем')
    else:
        messages.error(request, 'Нельзя изменить роль администратора')
    user.save()
    return redirect(reverse('admin_dashboard') + '?tab=users')

@admin_required
def admin_change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменён')
        else:
            messages.error(request, 'Исправьте ошибки в форме')
    return redirect(reverse('admin_dashboard') + '?tab=settings')

@admin_required
def admin_change_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('new_email')
        password = request.POST.get('password')
        user = request.user
        if not user.check_password(password):
            messages.error(request, 'Неверный пароль')
        elif User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
            messages.error(request, 'Этот email уже используется')
        else:
            user.email = new_email
            user.save()
            messages.success(request, 'Email успешно изменён')
    return redirect(reverse('admin_dashboard') + '?tab=settings')

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
    
    days = int(request.POST.get('days', 14)) if request.method == 'POST' else 14
    due_date = timezone.now().date() + timedelta(days=days)
    
    Loan.objects.create(
        reader=book_request.reader,
        book=book_request.book,
        due_date=due_date
    )
    
    book_request.book.status = 'on_loan'
    book_request.book.save()
    
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
    return redirect(reverse('dashboard') + '?tab=my_requests')

@login_required
def reader_profile(request):
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
    book = get_object_or_404(Book, book_id=book_id)
    reader_loan = None
    reader_request = None
    
    if request.user.is_authenticated and request.user.role == User.Roles.READER:
        reader_loan = Loan.objects.filter(
            reader=request.user, 
            book=book, 
            return_date__isnull=True
        ).first()
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

@login_required
def admin_panel(request):
    """Главная панель администратора"""
    if request.user.role != User.Roles.ADMIN:
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')
    active_tab = request.GET.get('tab', 'overview')
    
    total_books = Book.objects.count()
    total_users = User.objects.filter(role=User.Roles.READER).count()
    total_librarians = User.objects.filter(role=User.Roles.LIBRARIAN).count()
    total_loans = Loan.objects.count()
    overdue_loans = Loan.get_overdue_loans().count()
    
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
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="books_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
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
    if request.user.role != User.Roles.ADMIN:
        messages.error(request, 'Доступ запрещён.')
        return redirect('dashboard')
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
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
        messages.error(request, 'Ошибка')

    return redirect('dashboard')

@login_required
def change_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('new_email')
        password = request.POST.get('password')
        user = request.user
        
        # Проверяем пароль
        if not user.check_password(password):
            messages.error(request, 'Неверный пароль')
        elif User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
            messages.error(request, 'Этот email уже используется')
        elif User.objects.filter(username=new_email).exclude(pk=user.pk).exists():
            messages.error(request, 'Этот email уже используется')
        else:
            user.email = new_email
            user.username = new_email
            user.save()
            messages.success(request, 'Email успешно изменен!')
            
        return redirect('dashboard?tab=settings')
    
    return redirect('dashboard?tab=settings')

@login_required
def change_email_page(request):
    return render(request, 'change_email.html')

def generate_2fa_code():
    return str(random.randint(100000, 999999))

def send_2fa_code(email, code):
    subject = 'Код подтверждения для входа в АБИС'
    message = render_to_string('2fa_email.html', {'code': code})
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
        html_message=message,
    )