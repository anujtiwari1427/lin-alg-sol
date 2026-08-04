/* =========================================================
   LINEAR ALGEBRA SOLVER - MAIN JAVASCRIPT SYSTEM
   THEMES: 'green' (Cyber Green & Yellow), 'ocean' (Deep Navy & Slate), 'butter' (Forest Green & Butter), 'burgundy' (Black & Burgundy), 'light'
   ========================================================= */

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initSidebar();
  initGlobalSearch();
  initKeyboardShortcuts();
  highlightActiveNavLink();
});

const THEMES = ['green', 'ocean', 'butter', 'burgundy', 'light'];

function initTheme() {
  const saved = localStorage.getItem('las-theme') || 'green';
  applyTheme(saved, false);

  document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'green';
      const idx = THEMES.indexOf(current);
      const nextTheme = THEMES[(idx + 1) % THEMES.length];
      applyTheme(nextTheme, true);
      showToast(`Switched to ${nextTheme.toUpperCase()} theme`, 'info');
    });
  });
}

function applyTheme(theme, save = true) {
  document.documentElement.setAttribute('data-theme', theme);
  if (save) localStorage.setItem('las-theme', theme);

  document.querySelectorAll('.theme-toggle-btn i').forEach(icon => {
    icon.style.color = '';
    if (theme === 'green') {
      icon.className = 'fas fa-leaf text-success';
    } else if (theme === 'ocean') {
      icon.className = 'fas fa-water';
      icon.style.color = '#69818D';
    } else if (theme === 'butter') {
      icon.className = 'fas fa-sun';
      icon.style.color = '#FFEFB3';
    } else if (theme === 'burgundy') {
      icon.className = 'fas fa-wine-glass';
      icon.style.color = '#c47a8a';

    } else {
      icon.className = 'fas fa-moon text-primary';
    }
  });

  // Update the dashboard chart if it exists
  if (typeof window.updateChartTheme === 'function') {
    window.updateChartTheme(theme);
  }
}

function initSidebar() {
  // Mobile sidebar is handled by Bootstrap Offcanvas via data-bs-toggle in navbar.html.
  // This function is kept as a hook for any future custom sidebar behaviour.
}

function highlightActiveNavLink() {
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && (currentPath === href || (href !== '/' && currentPath.startsWith(href)))) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}

function initGlobalSearch() {
  const searchInput  = document.getElementById('globalSearchInput');
  const resultsBox   = document.getElementById('searchResultsContainer');

  if (!searchInput || !resultsBox) return;

  let debounceTimer;

  searchInput.addEventListener('input', e => {
    clearTimeout(debounceTimer);
    const query = e.target.value.trim();

    if (query.length < 2) {
      hideResults(resultsBox);
      return;
    }

    debounceTimer = setTimeout(() => {
      fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(r => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          return r.json();
        })
        .then(data => renderSearchResults(data.results, query, resultsBox))
        .catch(err => {
          console.error('[Search] Fetch error:', err);
          hideResults(resultsBox);
        });
    }, 250);
  });

  document.addEventListener('click', e => {
    if (!e.target.closest('.search-bar-container')) hideResults(resultsBox);
  });

  searchInput.addEventListener('focus', () => {
    if (searchInput.value.trim().length >= 2 && resultsBox.innerHTML) {
      resultsBox.style.display = 'block';
    }
  });
}

function renderSearchResults(results, query, container) {
  if (!container) return;

  if (!results || results.length === 0) {
    container.innerHTML = `
      <div class="p-3 text-center text-muted small">
        <i class="fas fa-search me-1"></i> No topics found for <strong>"${escapeHTML(query)}"</strong>
      </div>`;
  } else {
    container.innerHTML = results.map(item => `
      <a href="${escapeHTML(item.url)}" class="search-result-item">
        <div>
          <div class="fw-semibold text-primary-accent small">${escapeHTML(item.title)}</div>
          <small class="text-muted">${escapeHTML(item.category)}</small>
        </div>
        <i class="fas fa-chevron-right text-muted" style="font-size:0.7rem;"></i>
      </a>
    `).join('');
  }

  container.style.display = 'block';
}

function hideResults(container) {
  if (container) container.style.display = 'none';
}

function initKeyboardShortcuts() {
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      const searchInput = document.getElementById('globalSearchInput');
      if (searchInput) {
        searchInput.focus();
        searchInput.select();
      }
    }
  });
}

function showToast(message, type = 'info') {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    Object.assign(container.style, {
      position: 'fixed', bottom: '24px', right: '24px', zIndex: '9999',
      display: 'flex', flexDirection: 'column', gap: '8px'
    });
    document.body.appendChild(container);
  }

  const bgMap = { success: 'bg-success', danger: 'bg-danger', warning: 'bg-warning', info: 'bg-primary' };
  const bgClass = bgMap[type] || 'bg-primary';

  const toast = document.createElement('div');
  toast.className = `toast align-items-center text-white ${bgClass} border-0 show`;
  toast.style.cssText = 'min-width:240px; animation: fadeInUp 0.3s ease;';
  toast.setAttribute('role', 'alert');
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${escapeHTML(String(message))}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto"
              onclick="this.closest('.toast').remove()"></button>
    </div>`;

  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

function escapeHTML(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
