(function () {
  const root = document.documentElement;
  const body = document.body;

  function saveToStorage(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (error) {
      // ignore storage errors (private mode / blocked storage)
    }
  }

  function readFromStorage(key) {
    try {
      return localStorage.getItem(key);
    } catch (error) {
      return null;
    }
  }

  function removeFromStorage(key) {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      // ignore
    }
  }

  function debounce(callback, waitMs) {
    let timeoutId = null;
    return function debounced() {
      const context = this;
      const args = arguments;
      clearTimeout(timeoutId);
      timeoutId = setTimeout(function () {
        callback.apply(context, args);
      }, waitMs);
    };
  }

  function initThemeToggle() {
    const toggle = document.getElementById('themeToggle');
    const key = 'cineticket_theme';

    function applyTheme(theme) {
      root.setAttribute('data-theme', theme);
      if (body) {
        body.setAttribute('data-theme', theme);
      }
      if (toggle) {
        toggle.setAttribute('aria-pressed', String(theme === 'light'));
      }
    }

    const saved = readFromStorage(key);
    if (saved === 'light' || saved === 'dark') {
      applyTheme(saved);
    } else {
      applyTheme('dark');
    }

    if (!toggle) {
      return;
    }

    toggle.addEventListener('click', function () {
      const current = body && body.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      saveToStorage(key, next);
    });
  }

  function initNavbarToggle() {
    const toggle = document.querySelector('[data-navbar-toggle]');
    const targetSelector = toggle ? toggle.getAttribute('data-bs-target') : null;
    const collapse = targetSelector ? document.querySelector(targetSelector) : null;

    if (!toggle || !collapse) {
      return;
    }

    function setExpanded(isExpanded) {
      toggle.setAttribute('aria-expanded', String(isExpanded));
      collapse.classList.toggle('show', isExpanded);
    }

    toggle.addEventListener('click', function () {
      const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
      setExpanded(!isExpanded);
    });

    collapse.querySelectorAll('.nav-link, .theme-toggle, .nav-logout-btn').forEach(function (item) {
      item.addEventListener('click', function () {
        if (window.innerWidth < 992) {
          setExpanded(false);
        }
      });
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth >= 992) {
        setExpanded(false);
      }
    });
  }

  function initCarousels() {
    const carousels = document.querySelectorAll('[data-carousel]');
    carousels.forEach(function (carousel) {
      const slides = carousel.querySelectorAll('[data-carousel-slide]');
      const dots = carousel.querySelectorAll('[data-carousel-dot]');
      if (slides.length <= 1) {
        return;
      }

      let index = 0;
      let intervalId = null;
      const intervalMs = Number(carousel.getAttribute('data-interval')) || 2800;
      carousel.setAttribute('tabindex', '0');

      function setActive(nextIndex) {
        slides[index].classList.remove('is-active');
        if (dots[index]) {
          dots[index].classList.remove('is-active');
        }

        index = (nextIndex + slides.length) % slides.length;
        slides[index].classList.add('is-active');
        if (dots[index]) {
          dots[index].classList.add('is-active');
        }
      }

      function startAutoplay() {
        if (intervalId !== null) {
          return;
        }
        intervalId = setInterval(function () {
          setActive(index + 1);
        }, intervalMs);
      }

      function stopAutoplay() {
        if (intervalId === null) {
          return;
        }
        clearInterval(intervalId);
        intervalId = null;
      }

      dots.forEach(function (dot, dotIndex) {
        dot.addEventListener('click', function () {
          setActive(dotIndex);
        });
      });

      carousel.addEventListener('mouseenter', stopAutoplay);
      carousel.addEventListener('mouseleave', startAutoplay);
      carousel.addEventListener('focusin', stopAutoplay);
      carousel.addEventListener('focusout', startAutoplay);

      carousel.addEventListener('keydown', function (event) {
        if (event.key === 'ArrowRight') {
          setActive(index + 1);
        }
        if (event.key === 'ArrowLeft') {
          setActive(index - 1);
        }
      });

      startAutoplay();
    });
  }

  function initMessages() {
    const messages = document.querySelectorAll('.messages .message');
    messages.forEach(function (messageNode) {
      if (!messageNode.querySelector('.message-close-btn')) {
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'message-close-btn';
        closeButton.setAttribute('aria-label', 'Закрыть уведомление');
        closeButton.textContent = '×';
        closeButton.addEventListener('click', function () {
          messageNode.classList.add('is-hidden');
          setTimeout(function () {
            messageNode.remove();
          }, 220);
        });
        messageNode.appendChild(closeButton);
      }

      setTimeout(function () {
        if (!messageNode.isConnected) {
          return;
        }
        messageNode.classList.add('is-hidden');
        setTimeout(function () {
          messageNode.remove();
        }, 220);
      }, 5000);
    });
  }

  function initScrollTopButton() {
    const button = document.getElementById('scrollTopButton');
    if (!button) {
      return;
    }

    function updateState() {
      if (window.scrollY > 380) {
        button.classList.add('is-visible');
      } else {
        button.classList.remove('is-visible');
      }
    }

    button.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    window.addEventListener('scroll', updateState, { passive: true });
    updateState();
  }

  function initPasswordToggle() {
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(function (inputNode) {
      if (inputNode.dataset.passwordEnhanced === '1') {
        return;
      }
      inputNode.dataset.passwordEnhanced = '1';

      const wrapper = document.createElement('div');
      wrapper.className = 'password-field-wrap';
      inputNode.parentNode.insertBefore(wrapper, inputNode);
      wrapper.appendChild(inputNode);

      const toggleButton = document.createElement('button');
      toggleButton.type = 'button';
      toggleButton.className = 'password-toggle-btn';
      toggleButton.textContent = 'Показать';
      toggleButton.setAttribute('aria-label', 'Показать пароль');

      toggleButton.addEventListener('click', function () {
        const isPassword = inputNode.getAttribute('type') === 'password';
        inputNode.setAttribute('type', isPassword ? 'text' : 'password');
        toggleButton.textContent = isPassword ? 'Скрыть' : 'Показать';
        toggleButton.setAttribute('aria-label', isPassword ? 'Скрыть пароль' : 'Показать пароль');
      });

      wrapper.appendChild(toggleButton);
    });
  }

  function initAriaTooltips() {
    const elements = document.querySelectorAll('[aria-label]');
    elements.forEach(function (element) {
      if (!element.getAttribute('title')) {
        element.setAttribute('title', element.getAttribute('aria-label'));
      }
    });
  }

  function initConfirmActions() {
    const forms = document.querySelectorAll('form[data-confirm]');
    forms.forEach(function (form) {
      form.addEventListener('submit', function (event) {
        const message = form.dataset.confirm || 'Вы уверены?';
        if (!window.confirm(message)) {
          event.preventDefault();
        }
      });
    });
  }

  function initPostFormsProtection() {
    const forms = document.querySelectorAll('form[method="post"]:not(.favorite-form)');
    forms.forEach(function (form) {
      form.addEventListener('submit', function (event) {
        if (event.defaultPrevented) {
          return;
        }

        if (form.dataset.submitted === '1') {
          event.preventDefault();
          return;
        }

        if (typeof form.checkValidity === 'function' && !form.checkValidity()) {
          return;
        }

        form.dataset.submitted = '1';
        const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
        submitButtons.forEach(function (button) {
          if (button.tagName === 'BUTTON') {
            button.dataset.originalText = button.textContent;
            button.textContent = button.dataset.loadingText || 'Отправка...';
          } else if (button.tagName === 'INPUT') {
            button.dataset.originalValue = button.value;
            button.value = button.dataset.loadingText || 'Отправка...';
          }
          button.disabled = true;
        });
      });
    });
  }

  function initMovieFilters() {
    const form = document.querySelector('.movies-filters');
    if (!form) {
      return;
    }

    const storageKey = 'cineticket_movies_filters';
    const fields = Array.from(form.querySelectorAll('input[name], select[name]'));
    const searchInput = form.querySelector('input[name="q"]');
    const ageSelect = form.querySelector('select[name="age"]');
    const resetButton = form.querySelector('[data-filters-reset]');

    if (window.location.search.length <= 1) {
      const savedRaw = readFromStorage(storageKey);
      if (savedRaw) {
        try {
          const saved = JSON.parse(savedRaw);
          fields.forEach(function (field) {
            if (Object.prototype.hasOwnProperty.call(saved, field.name)) {
              field.value = saved[field.name];
            }
          });
        } catch (error) {
          removeFromStorage(storageKey);
        }
      }
    }

    function saveFilters() {
      const state = {};
      fields.forEach(function (field) {
        state[field.name] = field.value;
      });
      saveToStorage(storageKey, JSON.stringify(state));
    }

    fields.forEach(function (field) {
      field.addEventListener('change', saveFilters);
    });

    if (searchInput) {
      searchInput.addEventListener(
        'input',
        debounce(function () {
          saveFilters();
          form.requestSubmit();
        }, 450)
      );
    }

    if (ageSelect) {
      ageSelect.addEventListener('change', function () {
        saveFilters();
        form.requestSubmit();
      });
    }

    if (resetButton) {
      resetButton.addEventListener('click', function () {
        removeFromStorage(storageKey);
      });
    }
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }

    return new Promise(function (resolve, reject) {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();

      try {
        const successful = document.execCommand('copy');
        if (!successful) {
          throw new Error('copy failed');
        }
        resolve();
      } catch (error) {
        reject(error);
      } finally {
        textarea.remove();
      }
    });
  }

  function initMovieLinkCopy() {
    const button = document.querySelector('[data-copy-movie-link]');
    if (!button) {
      return;
    }

    const defaultText = button.textContent;
    button.addEventListener('click', function () {
      copyText(window.location.href)
        .then(function () {
          button.textContent = 'Ссылка скопирована';
        })
        .catch(function () {
          button.textContent = 'Не удалось скопировать';
        })
        .finally(function () {
          setTimeout(function () {
            button.textContent = defaultText;
          }, 1700);
        });
    });
  }

  function initTicketPricePreview() {
    const typeField = document.getElementById('id_ticket_type');
    const quantityField = document.getElementById('id_quantity');
    const adultField = document.getElementById('id_adult_qty');
    const studentField = document.getElementById('id_student_qty');
    const childField = document.getElementById('id_child_qty');
    const totalNode = document.querySelector('[data-ticket-total]');
    const hasLegacyForm = typeField && quantityField;
    const hasFamilyForm = adultField && studentField && childField;

    if (!totalNode || (!hasLegacyForm && !hasFamilyForm)) {
      return;
    }

    const priceMap = {};
    document.querySelectorAll('[data-ticket-code][data-ticket-price]').forEach(function (item) {
      const code = item.getAttribute('data-ticket-code');
      const price = Number(item.getAttribute('data-ticket-price'));
      if (code && Number.isFinite(price)) {
        priceMap[code] = price;
      }
    });

    function updateTotal() {
      if (hasFamilyForm) {
        const adultQty = Number(adultField.value || 0);
        const studentQty = Number(studentField.value || 0);
        const childQty = Number(childField.value || 0);

        const values = [adultQty, studentQty, childQty];
        const hasInvalid = values.some(function (value) {
          return !Number.isInteger(value) || value < 0 || value > 20;
        });
        if (hasInvalid) {
          totalNode.textContent = 'Проверьте количество билетов (от 0 до 20).';
          return;
        }

        const total =
          (priceMap.adult || 0) * adultQty +
          (priceMap.student || 0) * studentQty +
          (priceMap.child || 0) * childQty;

        const totalTickets = adultQty + studentQty + childQty;
        if (totalTickets === 0) {
          totalNode.textContent = 'Выберите хотя бы 1 билет.';
          return;
        }
        totalNode.textContent = 'Итого к оплате: ' + total + ' ₸';
        return;
      }

      const quantity = Number(quantityField.value);
      if (!Number.isInteger(quantity) || quantity < 1 || quantity > 10) {
        quantityField.setCustomValidity('Количество должно быть от 1 до 10.');
        totalNode.textContent = 'Проверьте количество билетов (от 1 до 10).';
        return;
      }
      quantityField.setCustomValidity('');

      const pricePerTicket = priceMap[typeField.value] || 0;
      const total = pricePerTicket * quantity;
      totalNode.textContent = 'Итого к оплате: ' + total + ' ₸';
    }

    if (hasLegacyForm) {
      typeField.addEventListener('change', updateTotal);
      quantityField.addEventListener('input', updateTotal);
    }
    if (hasFamilyForm) {
      adultField.addEventListener('input', updateTotal);
      studentField.addEventListener('input', updateTotal);
      childField.addEventListener('input', updateTotal);
    }
    updateTotal();
  }

  function initFaqBehavior() {
    const faqItems = document.querySelectorAll('.faq-item');
    if (!faqItems.length) {
      return;
    }

    const storageKey = 'cineticket_faq_open';
    const savedIndex = Number(readFromStorage(storageKey));
    if (Number.isInteger(savedIndex) && savedIndex >= 0 && savedIndex < faqItems.length) {
      faqItems.forEach(function (item, index) {
        item.open = index === savedIndex;
      });
    }

    faqItems.forEach(function (item, itemIndex) {
      item.addEventListener('toggle', function () {
        if (!item.open) {
          return;
        }

        faqItems.forEach(function (otherItem, otherIndex) {
          if (otherIndex !== itemIndex) {
            otherItem.open = false;
          }
        });
        saveToStorage(storageKey, String(itemIndex));
      });
    });
  }

  function initLazyImages() {
    const images = document.querySelectorAll('img');
    images.forEach(function (image) {
      if (!image.hasAttribute('loading')) {
        image.setAttribute('loading', 'lazy');
      }
      image.setAttribute('decoding', 'async');
    });
  }

  function initRevealOnScroll() {
    const cards = document.querySelectorAll(
      '.quick-card, .featured-card, .home-carousel, .movie-item-card, .schedule-card, .cinema-card, .contact-card, .faq-item'
    );
    if (!cards.length) {
      return;
    }

    cards.forEach(function (card) {
      card.classList.add('js-reveal');
    });

    if (!('IntersectionObserver' in window)) {
      cards.forEach(function (card) {
        card.classList.add('is-visible');
      });
      return;
    }

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) {
            return;
          }
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        });
      },
      {
        threshold: 0.1,
      }
    );

    cards.forEach(function (card) {
      observer.observe(card);
    });
  }

  function initSmoothAnchors() {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(function (link) {
      link.addEventListener('click', function (event) {
        const targetId = link.getAttribute('href');
        if (!targetId || targetId.length < 2) {
          return;
        }
        const target = document.querySelector(targetId);
        if (!target) {
          return;
        }

        event.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  }

  initThemeToggle();
  initNavbarToggle();
  initCarousels();
  initMessages();
  initScrollTopButton();
  initPasswordToggle();
  initAriaTooltips();
  initConfirmActions();
  initPostFormsProtection();
  initMovieFilters();
  initMovieLinkCopy();
  initTicketPricePreview();
  initFaqBehavior();
  initLazyImages();
  initRevealOnScroll();
  initSmoothAnchors();
})();

