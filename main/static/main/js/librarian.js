/**
 * Librarian Dashboard - Main JavaScript
 * Handles tab switching, section toggling, modal dialogs, and utility functions
 */

// ============================================================================
// TAB MANAGEMENT
// ============================================================================

/**
 * Switch between main tabs (Issuances, Catalog, Settings)
 * @param {string} tabName - The name of the tab to switch to
 */
function switchTab(tabName) {
  // Hide all tabs
  document.querySelectorAll('.tab-content').forEach(el => {
    el.classList.remove('active');
  });

  // Show selected tab
  const selectedTab = document.getElementById('tab-' + tabName);
  if (selectedTab) {
    selectedTab.classList.add('active');
  }

  // Update nav buttons
  document.querySelectorAll('.nav-tab').forEach(btn => {
    btn.classList.remove('active');
  });
  document.querySelector(`.nav-tab[data-tab="${tabName}"]`)?.classList.add('active');
}

// ============================================================================
// CARD DETAILS TOGGLE
// ============================================================================

/**
 * Toggle visibility of card details
 * @param {HTMLElement|Event} cardOrEvent - The card element or click event
 */
function toggleCardDetails(cardOrEvent) {
  let card;
  
  // Handle both direct card element and event
  if (cardOrEvent instanceof Event) {
    card = cardOrEvent.currentTarget;
  } else {
    card = cardOrEvent;
  }

  const details = card.querySelector('.card-details');
  const expandIcon = card.querySelector('.expand-icon');

  if (!details) return;

  card.classList.toggle('expanded');
  
  if (details.style.display === 'none' || !details.style.display) {
    details.style.display = 'block';
  } else {
    details.style.display = 'none';
  }
}

// ============================================================================
// MODAL WINDOW (Approve with days)
// ============================================================================

let currentApproveUrl = ''; // Stores the URL for the current approval

/**
 * Open modal to enter number of days for approval
 * @param {HTMLElement} button - The button that triggered the modal
 * @param {string} approveUrl - The URL to submit the approval
 */
function openApproveDaysModal(button, approveUrl) {
  currentApproveUrl = approveUrl;
  const modal = document.getElementById('approveDaysModal');
  if (modal) {
    modal.classList.add('open');
    // Focus the input
    setTimeout(() => document.getElementById('daysInput')?.focus(), 100);
  }
}

/**
 * Close modal by ID
 * @param {string} modalId - ID of the modal to close
 */
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('open');
  }
}

/**
 * Submit approval with days from modal input
 */
function submitApproveWithDays() {
  const daysInput = document.getElementById('daysInput');
  if (!daysInput) return;

  const days = parseInt(daysInput.value, 10);
  if (isNaN(days) || days < 1 || days > 365) {
    showToast('Количество дней должно быть от 1 до 365', 'warning');
    return;
  }

  if (!currentApproveUrl) {
    showToast('Ошибка: не указан URL запроса', 'error');
    return;
  }

  // Create a hidden form to POST
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = currentApproveUrl;

  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
  if (csrfToken) {
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);
  }

  const daysInputHidden = document.createElement('input');
  daysInputHidden.type = 'hidden';
  daysInputHidden.name = 'days';
  daysInputHidden.value = days;
  form.appendChild(daysInputHidden);

  document.body.appendChild(form);
  form.submit();

  closeModal('approveDaysModal');
}

// ============================================================================
// TOAST NOTIFICATIONS
// ============================================================================

/**
 * Display a toast notification message
 * @param {string} message - The message to display
 * @param {string} type - Type of notification: 'success', 'error', 'info', 'warning'
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.getElementById('toast');

  if (!toast) return;

  // Set message and styling based on type
  toast.textContent = message;
  toast.classList.remove('show', 'success', 'error', 'info', 'warning');

  // Apply color based on type
  if (type === 'success') {
    toast.style.background = '#10b981';
  } else if (type === 'error') {
    toast.style.background = '#ef4444';
  } else if (type === 'warning') {
    toast.style.background = '#f59e0b';
  } else {
    toast.style.background = '#1f2937';
  }

  // Show toast
  toast.classList.add('show');

  // Hide after duration
  setTimeout(() => {
    toast.classList.remove('show');
  }, duration);
}

// ============================================================================
// SETTINGS PAGE - PASSWORD CHANGE
// ============================================================================

/**
 * Save new password (placeholder implementation, integrate with your backend)
 */
function savePassword() {
  const current = document.getElementById('pwd-current')?.value;
  const newPwd = document.getElementById('pwd-new')?.value;
  const confirm = document.getElementById('pwd-confirm')?.value;

  // Validation
  if (!current || !newPwd || !confirm) {
    showToast('Заполните все поля', 'warning');
    return;
  }

  if (newPwd !== confirm) {
    showToast('Пароли не совпадают', 'error');
    return;
  }

  if (newPwd.length < 8) {
    showToast('Пароль должен быть не менее 8 символов', 'warning');
    return;
  }

  // Here you would typically send an AJAX request to the server
  // For demonstration, we'll just show a message
  showToast('Функция изменения пароля в разработке', 'info');
  
  // Clear fields
  document.getElementById('pwd-current').value = '';
  document.getElementById('pwd-new').value = '';
  document.getElementById('pwd-confirm').value = '';
}

// ============================================================================
// SETTINGS PAGE - EMAIL CHANGE
// ============================================================================

/**
 * Save new email (placeholder implementation, integrate with your backend)
 */
function saveEmail() {
  const newEmail = document.getElementById('new-email')?.value;

  // Validation
  if (!newEmail) {
    showToast('Введите новый email', 'warning');
    return;
  }

  // Simple email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(newEmail)) {
    showToast('Введите корректный email', 'error');
    return;
  }

  // Here you would typically send an AJAX request to the server
  showToast('Функция изменения email в разработке', 'info');
  
  // Clear field
  document.getElementById('new-email').value = '';
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Format date to Russian format (dd.mm.yyyy)
 * @param {Date|string} date - Date object or string
 * @returns {string} Formatted date
 */
function formatDate(date) {
  const d = new Date(date);
  const day = String(d.getDate()).padStart(2, '0');
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const year = d.getFullYear();
  return `${day}.${month}.${year}`;
}

/**
 * Get number of days between two dates
 * @param {Date} date1 - First date
 * @param {Date} date2 - Second date
 * @returns {number} Number of days
 */
function daysBetween(date1, date2) {
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  const time = Math.abs(d2 - d1);
  const days = Math.ceil(time / (1000 * 60 * 60 * 24));
  return days;
}

// ============================================================================
// EVENT LISTENERS & INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
  // --- Navigation tab listeners ---
  document.querySelectorAll('.nav-tab').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const tabName = this.dataset.tab;
      if (tabName) switchTab(tabName);
    });
  });

  // Set default active tab if none is active (fallback)
  const activeTab = document.querySelector('.nav-tab.active');
  if (!activeTab) {
    // Activate first tab (issuances)
    const firstTab = document.querySelector('.nav-tab[data-tab="issuances"]');
    if (firstTab) {
      firstTab.classList.add('active');
      switchTab('issuances');
    }
  } else {
    // Ensure tab content matches the active button
    const tabName = activeTab.dataset.tab;
    if (tabName) switchTab(tabName);
  }

  // --- Modal close on outside click ---
  const modal = document.getElementById('approveDaysModal');
  if (modal) {
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        closeModal('approveDaysModal');
      }
    });
  }

  // --- Close toast when clicked ---
  const toast = document.getElementById('toast');
  if (toast) {
    toast.addEventListener('click', function() {
      this.classList.remove('show');
    });
  }

  // --- Keyboard shortcuts ---
  document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + 1,2,3 for tabs
    if ((e.ctrlKey || e.metaKey) && !isNaN(parseInt(e.key))) {
      const num = parseInt(e.key);
      if (num >= 1 && num <= 3) {
        e.preventDefault();
        const tabs = ['issuances', 'catalog', 'settings'];
        switchTab(tabs[num - 1]);
      }
    }
    // Escape closes modal and toast
    if (e.key === 'Escape') {
      closeModal('approveDaysModal');
      if (toast) toast.classList.remove('show');
    }
  });
});