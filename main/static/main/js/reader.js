function filterBooks() {
    const searchText = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const activeFilter = document.querySelector('.chip.active')?.dataset.filter || 'all';
    // Ищем все карточки книг (и .book-item, и .book-card)
    const books = document.querySelectorAll('.book-item, .book-card');
    
    books.forEach(book => {
        const title = book.querySelector('h3')?.innerText.toLowerCase() || '';
        const authorElem = book.querySelector('p');
        const author = authorElem ? authorElem.innerText.toLowerCase() : '';
        const status = book.dataset.status;
        
        let matchesSearch = title.includes(searchText) || author.includes(searchText);
        let matchesFilter = true;
        
        if (activeFilter === 'available') matchesFilter = (status === 'available');
        else if (activeFilter === 'issued') matchesFilter = (status === 'on_loan');
        else if (activeFilter === 'unavailable') matchesFilter = (status === 'reserved');
        
        book.style.display = (matchesSearch && matchesFilter) ? 'block' : 'none';
    });
}

// Переключение вкладок (только если они есть на странице)
if (document.querySelector('.nav-tab')) {
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            window.location.href = "?tab=" + tabName;
        });
    });
}

// Переключение фильтров (чипсы)
if (document.querySelector('.chip')) {
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', function() {
            document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            filterBooks();
        });
    });
}

// При загрузке страницы вешаем обработчик на поле поиска (если есть)
if (document.getElementById('searchInput')) {
    document.getElementById('searchInput').addEventListener('input', filterBooks);
}