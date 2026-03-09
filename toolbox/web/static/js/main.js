/* ─── Theme ──────────────────────────────────────────────────── */
const ThemeManager = {
  STORAGE_KEY: 'toolbox_theme',

  init() {
    const saved = localStorage.getItem(this.STORAGE_KEY) || 'system';
    this.apply(saved);
  },

  apply(theme) {
    const root = document.documentElement;
    if (theme === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
      root.setAttribute('data-theme', theme);
    }
    localStorage.setItem(this.STORAGE_KEY, theme);
  },

  cycle() {
    const current = localStorage.getItem(this.STORAGE_KEY) || 'system';
    const themes = ['light', 'dark', 'system'];
    const next = themes[(themes.indexOf(current) + 1) % themes.length];
    this.apply(next);
    return next;
  }
};

/* ─── Sidebar ────────────────────────────────────────────────── */
const Sidebar = {
  STORAGE_KEY: 'toolbox_sidebar_collapsed',

  init() {
    const collapsed = localStorage.getItem(this.STORAGE_KEY) === 'true';
    if (collapsed) this.collapse(false);
  },

  toggle() {
    const sidebar = document.getElementById('sidebar');
    const isCollapsed = sidebar.classList.contains('collapsed');
    isCollapsed ? this.expand() : this.collapse();
  },

  collapse(save = true) {
    const sidebar = document.getElementById('sidebar');
    const icon = document.getElementById('toggleIcon');
    sidebar.classList.add('collapsed');
    icon.classList.replace('fa-angles-left', 'fa-angles-right');
    if (save) localStorage.setItem(this.STORAGE_KEY, 'true');
  },

  expand() {
    const sidebar = document.getElementById('sidebar');
    const icon = document.getElementById('toggleIcon');
    sidebar.classList.remove('collapsed');
    icon.classList.replace('fa-angles-right', 'fa-angles-left');
    localStorage.setItem(this.STORAGE_KEY, 'false');
  }
};

/* ─── Modals ─────────────────────────────────────────────────── */
const Modal = {
  open(id) {
    document.getElementById(id).classList.add('open');
  },

  close(id) {
    document.getElementById(id).classList.remove('open');
  },

  closeAll() {
    document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('open'));
  }
};

/* ─── API ────────────────────────────────────────────────────── */
const Api = {
  async get(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`GET ${url} failed: ${res.status}`);
    return res.json();
  },

  async post(url, data = {}) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`POST ${url} failed: ${res.status}`);
    return res.json();
  },

  async put(url, data = {}) {
    const res = await fetch(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`PUT ${url} failed: ${res.status}`);
    return res.json();
  },

  async delete(url) {
    const res = await fetch(url, { method: 'DELETE' });
    if (!res.ok) throw new Error(`DELETE ${url} failed: ${res.status}`);
    return res.json();
  }
};

/* ─── Toast ──────────────────────────────────────────────────── */
const Toast = {
  show(message, type = 'info') {
    const existing = document.getElementById('toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <i class="fa-solid ${this._icon(type)}"></i>
      <span>${message}</span>
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  },

  success(msg) { this.show(msg, 'success'); },
  error(msg) { this.show(msg, 'error'); },
  warning(msg) { this.show(msg, 'warning'); },

  _icon(type) {
    return {
      success: 'fa-circle-check',
      error: 'fa-circle-xmark',
      warning: 'fa-triangle-exclamation',
      info: 'fa-circle-info'
    }[type] || 'fa-circle-info';
  }
};

/* ─── Init ───────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();
  Sidebar.init();

  // Sidebar toggle
  document.getElementById('sidebarToggle')?.addEventListener('click', (e) => {
    e.stopPropagation();
    Sidebar.toggle();
  });

  // Click su sidebar collassata per riaprirla
  document.getElementById('sidebar')?.addEventListener('click', () => {
    const sidebar = document.getElementById('sidebar');
    if (sidebar.classList.contains('collapsed')) Sidebar.expand();
  });

  // Theme toggle
  document.getElementById('themeToggle')?.addEventListener('click', () => {
    const next = ThemeManager.cycle();
    Toast.show(`Theme: ${next}`, 'info');
  });

  // Help modal
  document.getElementById('helpBtn')?.addEventListener('click', () => Modal.open('helpModal'));

  // About modal
  document.getElementById('aboutBtn')?.addEventListener('click', () => Modal.open('aboutModal'));

  // Close modals
  document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', () => Modal.close(btn.dataset.modal));
  });

  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) Modal.closeAll();
    });
  });
});
