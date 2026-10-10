/**
 * Enterprise Smart Library Management Platform
 * Frontend JavaScript API & UI Utilities
 */

const API_BASE = '/api';

// ─────────────────────────── UTILITY FUNCTIONS ──────────────────────────────

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function formatDate(iso) {
    if (!iso) return '—';
    try {
        return new Intl.DateTimeFormat('en-GB', {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit',
        }).format(new Date(iso));
    } catch {
        return iso;
    }
}

// ─────────────────────────── TOAST NOTIFICATIONS ────────────────────────────

function showToast(message, type = 'info', durationMs = 3500) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(8px)';
        toast.style.transition = 'opacity 0.3s, transform 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, durationMs);
}

// ─────────────────────────── MODAL HELPERS ──────────────────────────────────

function openConfirmModal(title, message, onConfirm) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-message').innerHTML = message;
    const confirmBtn = document.getElementById('modal-confirm-btn');
    confirmBtn.onclick = onConfirm;
    document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal-overlay').classList.add('hidden');
}

function openFormModal(title, bodyHtml, onSubmit) {
    document.getElementById('form-modal-title').textContent = title;
    document.getElementById('form-modal-body').innerHTML = bodyHtml;
    document.getElementById('form-modal-submit').onclick = onSubmit;
    document.getElementById('form-modal-overlay').classList.remove('hidden');
}

function closeFormModal() {
    document.getElementById('form-modal-overlay').classList.add('hidden');
}

// Close modals on overlay click
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('modal-overlay')?.addEventListener('click', function (e) {
        if (e.target === this) closeModal();
    });
    document.getElementById('form-modal-overlay')?.addEventListener('click', function (e) {
        if (e.target === this) closeFormModal();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') { closeModal(); closeFormModal(); }
    });
});

// ─────────────────────────── API FETCH WRAPPER ───────────────────────────────

async function apiFetch(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: { 'Content-Type': 'application/json', ...options.headers },
            ...options,
        });
        const data = await response.json();
        if (!response.ok) {
            const msg = data.error || `HTTP ${response.status}`;
            showToast(msg, 'error');
            return null;
        }
        return data;
    } catch (err) {
        showToast('Network error: ' + err.message, 'error');
        return null;
    }
}

// ─────────────────────────── API FUNCTIONS ──────────────────────────────────

async function getDashboardData() {
    return await apiFetch(`${API_BASE}/dashboard`);
}

async function getBooks() {
    const res = await apiFetch(`${API_BASE}/books`);
    return res ? res.books : null;
}

async function searchBooks(query = '') {
    const url = query
        ? `${API_BASE}/books?q=${encodeURIComponent(query)}`
        : `${API_BASE}/books`;
    const res = await apiFetch(url);
    return res ? res.books : null;
}

async function addBook(data) {
    const res = await apiFetch(`${API_BASE}/books`, {
        method: 'POST',
        body: JSON.stringify(data),
    });
    return res ? res.book : null;
}

async function getUsers() {
    const res = await apiFetch(`${API_BASE}/users`);
    return res ? res.users : null;
}

async function addUser(data) {
    const res = await apiFetch(`${API_BASE}/users`, {
        method: 'POST',
        body: JSON.stringify(data),
    });
    return res ? res.user : null;
}

async function deleteUser(userId) {
    return await apiFetch(`${API_BASE}/users/${encodeURIComponent(userId)}`, {
        method: 'DELETE',
    });
}

async function getLoans() {
    const res = await apiFetch(`${API_BASE}/loans`);
    return res ? res.loans : null;
}

async function borrowBook(userId, bookId) {
    const res = await apiFetch(`${API_BASE}/borrow`, {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, book_id: bookId }),
    });
    return res ? res.loan : null;
}

async function returnBook(userId, bookId) {
    return await apiFetch(`${API_BASE}/return`, {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, book_id: bookId }),
    });
}
