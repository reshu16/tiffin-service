// ── API Base URL ──────────────────────────────────────────────
const API = 'http://localhost:5000/api';

// ── Token Helpers ─────────────────────────────────────────────
const getToken  = () => localStorage.getItem('access_token');
const getUser   = () => JSON.parse(localStorage.getItem('user') || 'null');
const isLogged  = () => !!getToken();

// ── Auth Headers ──────────────────────────────────────────────
const authHeaders = () => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
});

// ── API Request Helper ────────────────────────────────────────
async function apiRequest(endpoint, method = 'GET', body = null, auth = false) {
    const headers = auth ? authHeaders() : { 'Content-Type': 'application/json' };
    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);

    try {
        const res  = await fetch(`${API}${endpoint}`, options);
        const data = await res.json();
        if (!res.ok) throw { status: res.status, message: data.error || 'Something went wrong' };
        return data;
    } catch (err) {
        throw err;
    }
}

// ── Toast Notification ────────────────────────────────────────
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container') ||
        (() => {
            const el = document.createElement('div');
            el.id = 'toast-container';
            el.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(el);
            return el;
        })();

    const id   = 'toast-' + Date.now();
    const icon = type === 'success' ? 'check-circle-fill' :
                 type === 'danger'  ? 'x-circle-fill' : 'info-circle-fill';

    container.innerHTML += `
        <div id="${id}" class="toast align-items-center text-bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-${icon} me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto"
                        data-bs-dismiss="toast"></button>
            </div>
        </div>`;

    const toast = new bootstrap.Toast(document.getElementById(id),
                                      { delay: 3500 });
    toast.show();
}

// ── Logout ────────────────────────────────────────────────────
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

// ── Update Navbar based on login state ───────────────────────
function updateNavbar() {
    const user      = getUser();
    const navGuest  = document.getElementById('nav-guest');
    const navUser   = document.getElementById('nav-user');
    const navName   = document.getElementById('nav-username');

    if (user && isLogged()) {
        navGuest?.classList.add('d-none');
        navUser?.classList.remove('d-none');
        if (navName) navName.textContent = user.full_name.split(' ')[0];
    } else {
        navGuest?.classList.remove('d-none');
        navUser?.classList.add('d-none');
    }
}

// ── Format Currency ───────────────────────────────────────────
const formatRupee = (amt) => `₹${parseFloat(amt).toFixed(2)}`;

// ── Format Date ───────────────────────────────────────────────
const formatDate = (iso) => new Date(iso).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric'
});

// ── Order Status Badge ────────────────────────────────────────
function statusBadge(status) {
    const labels = {
        pending:          'Pending',
        confirmed:        'Confirmed',
        preparing:        'Preparing',
        out_for_delivery: 'Out for Delivery',
        delivered:        'Delivered',
        cancelled:        'Cancelled'
    };
    return `<span class="badge status-${status} px-3 py-2 rounded-pill">
                ${labels[status] || status}
            </span>`;
}

// ── Redirect by role ──────────────────────────────────────────
function redirectByRole(role) {
    const routes = {
        admin:    '/admin/dashboard',
        kitchen:  '/kitchen/dashboard',
        delivery: '/delivery/dashboard',
        customer: '/dashboard'
    };
    window.location.href = routes[role] || '/';
}

// Run on every page
document.addEventListener('DOMContentLoaded', updateNavbar);