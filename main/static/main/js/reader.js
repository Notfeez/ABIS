(function() {
    'use strict';

    // ============================================================================
    // TAB SWITCHING
    // ============================================================================
    
    function initTabs() {
        const tabs = document.querySelectorAll('.nav-tab');
        const contents = document.querySelectorAll('.tab-content');

        function switchTab(tabId) {
            // Hide all tabs
            contents.forEach(c => c.classList.remove('active'));
            
            // Show selected tab
            const activeContent = document.getElementById(tabId);
            if (activeContent) {
                activeContent.classList.add('active');
                // Update URL without page reload
                const url = new URL(window.location);
                url.searchParams.set('tab', tabId);
                window.history.replaceState({}, '', url);
            }

            // Update button states
            tabs.forEach(btn => btn.classList.remove('active'));
            const activeBtn = Array.from(tabs).find(btn => btn.dataset.tab === tabId);
            if (activeBtn) activeBtn.classList.add('active');
        }

        tabs.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                switchTab(btn.dataset.tab);
            });
        });

        // Initialize with current tab from URL
        const currentTab = new URLSearchParams(window.location.search).get('tab') || 'catalog';
        switchTab(currentTab);
    }

    // ============================================================================
    // SEARCH & FILTER
    // ============================================================================
    
    function initSearch() {
        const searchInput = document.getElementById('searchInput');
        if (!searchInput) return;

        searchInput.addEventListener('input', filterBooks);
    }

    function filterBooks() {
        const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
        const books = document.querySelectorAll('.book-item');
        
        books.forEach(book => {
            const title = book.querySelector('h3')?.textContent.toLowerCase() || '';
            const author = book.querySelector('.book-author')?.textContent.toLowerCase() || '';
            const isbn = book.querySelector('.book-isbn')?.textContent.toLowerCase() || '';
            
            const matches = title.includes(searchTerm) || 
                          author.includes(searchTerm) || 
                          isbn.includes(searchTerm);
            
            book.style.display = matches ? 'block' : 'none';
        });
    }

    // ============================================================================
    // FILTER BY STATUS
    // ============================================================================
    
    function initStatusFilter() {
        document.querySelectorAll('.chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                // Remove active from all chips
                document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
                // Add active to clicked chip
                e.target.classList.add('active');
                
                filterByStatus(e.target.dataset.filter);
            });
        });
    }

    function filterByStatus(status) {
        const items = document.querySelectorAll('[data-status]');
        
        items.forEach(item => {
            let show = false;
            
            if (status === 'all') {
                show = true;
            } else if (status === 'available' && item.dataset.status === 'available') {
                show = true;
            } else if (status === 'issued' && item.dataset.status === 'on_loan') {
                show = true;
            } else if (status === 'unavailable' && (item.dataset.status === 'reserved' || item.dataset.status === 'on_loan')) {
                show = true;
            }
            
            item.style.display = show ? 'block' : 'none';
        });
    }

    // ============================================================================
    // TOAST NOTIFICATIONS
    // ============================================================================
    
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // ============================================================================
    // INITIALIZATION
    // ============================================================================
    
    document.addEventListener('DOMContentLoaded', () => {
        // Initialize all features
        initTabs();
        initSearch();
        initStatusFilter();
        
        // Show initial filter state
        filterByStatus('all');
        
        // Expose functions globally for inline handlers
        window.filterBooks = filterBooks;
        window.showToast = showToast;
    });

})();