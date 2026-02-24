(function () {
  const root = document.documentElement;
  const toggle = document.getElementById('themeToggle');
  const key = 'cineticket_theme';

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
  }

  const saved = localStorage.getItem(key);
  if (saved === 'light' || saved === 'dark') {
    applyTheme(saved);
  } else {
    applyTheme('dark');
  }

  if (toggle) {
    toggle.addEventListener('click', function () {
      const current = root.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      localStorage.setItem(key, next);
    });
  }
})();
