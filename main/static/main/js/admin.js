/**
 * Admin Dashboard JavaScript
 * Обеспечивает переключение вкладок, поиск пользователей и уведомления.
 */

document.addEventListener('DOMContentLoaded', function() {
    // --- Переключение вкладок ---
    const tabs = document.querySelectorAll('.nav-tab');
    const contents = document.querySelectorAll('.tab-content');

    function switchTab(tabId) {
        // Скрыть все вкладки
        contents.forEach(content => content.classList.remove('active'));
        // Показать выбранную
        const activeContent = document.getElementById('tab-' + tabId);
        if (activeContent) activeContent.classList.add('active');

        // Обновить классы на кнопках
        tabs.forEach(btn => btn.classList.remove('active'));
        const activeBtn = Array.from(tabs).find(btn => btn.dataset.tab === tabId);
        if (activeBtn) activeBtn.classList.add('active');

        // Обновить URL (параметр tab) без перезагрузки
        const url = new URL(window.location);
        url.searchParams.set('tab', tabId);
        window.history.replaceState({}, '', url);
    }

    tabs.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            switchTab(this.dataset.tab);
        });
    });

    // Инициализация из URL (если параметр tab передан)
    const urlParams = new URLSearchParams(window.location.search);
    const activeTabFromUrl = urlParams.get('tab');
    if (activeTabFromUrl) {
        const foundBtn = Array.from(tabs).find(btn => btn.dataset.tab === activeTabFromUrl);
        if (foundBtn) {
            switchTab(activeTabFromUrl);
        }
    }

    // --- Поиск пользователей ---
    const searchInput = document.getElementById('users-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('#users-table-body .user-row');

            rows.forEach(row => {
                const dataName = row.getAttribute('data-name') || '';
                if (dataName.toLowerCase().includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // --- Тосты (уведомления) ---
    const toast = document.getElementById('toast');
    if (toast) {
        window.showToast = function(message, type = 'info', duration = 3000) {
            toast.textContent = message;
            toast.classList.remove('show', 'success', 'error', 'warning');
            if (type === 'success') {
                toast.style.background = '#10b981';
            } else if (type === 'error') {
                toast.style.background = '#ef4444';
            } else if (type === 'warning') {
                toast.style.background = '#f59e0b';
            } else {
                toast.style.background = '#1e293b';
            }
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
            }, duration);
        };

        // Закрытие тоста по клику
        toast.addEventListener('click', function() {
            this.classList.remove('show');
        });
    }

    // Закрытие тоста по Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && toast && toast.classList.contains('show')) {
            toast.classList.remove('show');
        }
    });
});