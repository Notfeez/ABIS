/* ============================================================================
   АБИС — Библиотека | admin.js
   ============================================================================ */

const AdminUI = (() => {

  /* ── Tab switching ──────────────────────────────────────── */
  function switchTab(name) {
    document.querySelectorAll('.nav-tab').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === name);
    });
    document.querySelectorAll('.tab-content').forEach(section => {
      section.classList.toggle('active', section.id === `tab-${name}`);
    });
    // Sync URL so ?tab= stays readable (no reload)
    const url = new URL(window.location);
    url.searchParams.set('tab', name);
    history.replaceState(null, '', url);
  }

  /* ── Client-side card search ────────────────────────────── */
  function filterCards(inputId, listId) {
    const input = document.getElementById(inputId);
    const list  = document.getElementById(listId);
    if (!input || !list) return;

    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      list.querySelectorAll('.user-row-card').forEach(card => {
        card.style.display = (!q || card.textContent.toLowerCase().includes(q)) ? '' : 'none';
      });
    });
  }

  /* ── Books grid search ──────────────────────────────────── */
  function filterGrid(inputId, gridId) {
    const input = document.getElementById(inputId);
    const grid  = document.getElementById(gridId);
    if (!input || !grid) return;

    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      grid.querySelectorAll('.book-card').forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = (!q || text.includes(q)) ? '' : 'none';
      });
    });
  }

  /* ── Collapse toggle ────────────────────────────────────── */
  function toggleCollapse(bodyId) {
    const body   = document.getElementById(bodyId);
    const toggle = body?.previousElementSibling;
    if (!body) return;

    const isOpen = body.classList.toggle('open');
    if (toggle) toggle.classList.toggle('open', isOpen);
  }

  /* ── Toast ──────────────────────────────────────────────── */
  let _toastTimer = null;
  function showToast(msg, duration = 2800) {
    const el = document.getElementById('toast');
    if (!el) return;
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(_toastTimer);
    _toastTimer = setTimeout(() => el.classList.remove('show'), duration);
  }

  /* ── Django messages → toast ────────────────────────────── */
  function flashMessages() {
    const block = document.querySelector('.messages-block');
    if (!block) return;
    block.querySelectorAll('.alert').forEach(el => {
      showToast(el.textContent.trim());
    });
    // Hide the inline block after showing as toasts
    block.style.display = 'none';
  }

  /* ── Init ───────────────────────────────────────────────── */
  function init() {
    // Wire up nav tab clicks
    document.querySelectorAll('.nav-tab[data-tab]').forEach(btn => {
      btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // Search hooks
    filterCards('users-search', 'users-cards');
    filterGrid ('books-search', 'books-grid');

    // Show Django messages as toasts
    flashMessages();
  }

  document.addEventListener('DOMContentLoaded', init);

  /* Public */
  return { switchTab, toggleCollapse, showToast };

})();
