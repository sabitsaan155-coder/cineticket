# CineTicket

Учебный Django-проект для кино-афиши, расписания кинотеатров, избранного, отзывов и онлайн-покупки билетов.

## Что уже реализовано
- Регистрация, логин, логаут, профиль пользователя.
- Загрузка аватара с валидацией размера и типа файла.
- Смена пароля и восстановление пароля через стандартные Django auth views.
- Каталог фильмов, детальная страница фильма, фильтры и пагинация.
- Покупка билетов, включая семейную покупку с несколькими типами билетов в одном заказе.
- История покупок в профиле и отдельный раздел билетов.
- Избранное для авторизованных пользователей.
- Отзывы и рейтинг 1–5, средний рейтинг и количество отзывов.
- Разделы: главная, фильмы, расписание, кинотеатры, контакты, FAQ, о проекте.
- Форма обратной связи на странице контактов.
- Кастомный template tag для сохранения querystring при пагинации.
- Кастомные страницы ошибок 404/500.
- JSON API с endpoint'ами для фильмов, кинотеатров, сеансов и жанров.
- Расширенная Django admin: `list_display`, `search_fields`, `list_filter`, inline, actions, fieldsets, `prepopulated_fields`, `readonly_fields`.
- 21 JS-сценарий для UX и интерактивности.

## Stack
- Python 3.12+
- Django 5
- SQLite (локально)
- PostgreSQL (для прод-конфигурации)
- WhiteNoise
- Gunicorn

## Design Source

This project is based on the free HTML template:

Start Bootstrap – Modern Business  
https://startbootstrap.com/template/modern-business  
License: MIT

Source files used from the official template archive:
- `startbootstrap-modern-business-gh-pages/index.html` — source markup for navbar, hero and footer
- `startbootstrap-modern-business-gh-pages/css/styles.css` — copied to `static/css/vendor/modern-business/styles.css`
- `startbootstrap-modern-business-gh-pages/js/scripts.js` — copied to `static/js/vendor/modern-business/scripts.js`
- `startbootstrap-modern-business-gh-pages/assets/favicon.ico` — copied to `static/images/vendor/modern-business/favicon.ico`

Integrated sections:
- Base layout: navbar + footer
- Hero section on homepage
- Utility classes from template CSS

Customized in project:
- Django template blocks and URL routing
- auth links, profile link and theme toggle in navbar
- active menu states
- project-specific dark theme overrides in `static/css/main.css`
- existing page components and JS scenarios

## Запуск локально (Windows PowerShell)
1. Создать и активировать окружение:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Установить зависимости:
```powershell
pip install -r requirements.txt
```

3. Подготовить переменные окружения:
```powershell
Copy-Item .env.example .env
```

4. Применить миграции и создать суперпользователя:
```powershell
python manage.py migrate
python manage.py createsuperuser
```

5. Заполнить тестовые данные:
```powershell
python manage.py seed_cinema
```

6. Запустить сервер:
```powershell
python manage.py runserver
```

## Прод-минимум (без хостинга)
- Установить `DEBUG=0`.
- Указать `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`.
- Настроить `DATABASE_URL` на PostgreSQL.
- Выполнить:
```powershell
python manage.py migrate
python manage.py collectstatic
```
- Запуск через Gunicorn + Nginx.

## Logs
- Локально лог приложения пишется в `logs/django.log`.
- Просмотр лога в PowerShell:
```powershell
Get-Content .\logs\django.log -Wait
```

## Restart (local)
- Остановить локальный сервер: `Ctrl + C`
- Повторный запуск:
```powershell
python manage.py runserver
```

## Backup strategy
- Основной объект резервного копирования — база данных PostgreSQL.
- Минимальная стратегия:
  - ежедневный `pg_dump`,
  - хранение нескольких последних backup-файлов,
  - отдельное хранение резервных копий вне директории проекта.
- Пример команды:
```bash
pg_dump -U <db_user> -h <db_host> -Fc <db_name> > backup.dump
```
- Пример восстановления:
```bash
pg_restore -U <db_user> -d <db_name> backup.dump
```

## Линтинг и форматирование
- Ruff:
```powershell
ruff check .
```
- Black:
```powershell
black --check .
```

## Роли пользователей
- `user` — обычный пользователь сайта: регистрация, вход, покупки, избранное, отзывы, профиль.
- `manager` — контент-менеджер через Django Groups / Permissions: управление фильмами, сеансами, кинотеатрами и тарифами без полного superuser-доступа.
- `admin` — суперпользователь с полным доступом к проекту и админке.

## API
Базовый JSON API доступен по префиксу `/api/`.

### Endpoints
- `GET /api/movies/` — список фильмов.
- `GET /api/movies/<slug>/` — детали фильма.
- `GET /api/cinemas/` — список кинотеатров.
- `GET /api/cinemas/<slug>/` — детали кинотеатра.
- `GET /api/screenings/` — список сеансов.
- `GET /api/screenings/<id>/` — детали сеанса.
- `GET /api/genres/` — список жанров.

### Фильтры и параметры
- `search` — поиск по названию фильма.
- `genre` — фильтр по slug жанра.
- `age_rating` — фильтр по возрастному рейтингу.
- `ordering` — сортировка: `title`, `-title`, `release_year`, `-release_year`, `duration_min`, `-duration_min`.
- `cinema` — фильтр сеансов по кинотеатру.
- `date` — сеансы за конкретную дату (`YYYY-MM-DD`).
- `date_from`, `date_to` — диапазон дат.
- `limit`, `offset` — ограничение выборки.

### Защищённые методы
- `POST /api/movies/`
- `PUT/PATCH /api/movies/<slug>/`
- `DELETE /api/movies/<slug>/`

Изменяющие методы доступны только авторизованным `staff` пользователям.

### Формат ошибок
```json
{
  "error": {
    "code": "bad_request",
    "message": "Invalid ordering parameter."
  }
}
```

### Примеры запросов
```bash
curl "http://127.0.0.1:8000/api/movies/?search=dark&genre=drama&ordering=-release_year"
curl "http://127.0.0.1:8000/api/screenings/?cinema=aport-mall&date_from=2026-03-01&date_to=2026-03-31"
curl "http://127.0.0.1:8000/api/movies/the-godfather/"
```

## Чеклист соответствия требованиям
- [x] 10+ Django apps
- [x] Базовый layout (`base.html`) + активное меню
- [x] Пользователи: регистрация / логин / логаут
- [x] Профиль пользователя, аватар и история покупок
- [x] Пользователи и права доступа (`user`, `staff`, `admin`)
- [х] Отдельная прикладная роль `manager` подготовлена через Django Groups / Permissions, но ещё не выведена в отдельный пользовательский сценарий
- [x] Кастомные страницы 404/500
- [x] `.env.example`, `requirements.txt`, `.gitignore`
- [x] MEDIA/STATIC настроены, `collectstatic` предусмотрен
- [x] Пагинация и фильтры в каталоге
- [x] Полноценный API (5+ endpoints)
- [x] Расширенная админка по основным критериям
- [x] Password reset flow
- [x] Reviews + rating + average
- [x] 21 JS scenarios

## Текущий статус README
- README синхронизирован с текущим кодом проекта.
- Разделы `Logs`, `Restart (local)`, `Backup strategy`, `API`, `Admin`, `Password reset`, `Avatar upload` и `JS scenarios` актуализированы.
- Формулировки по ролям уточнены: полностью реализованы `user`, `staff`, `admin`; роль `manager` подготовлена на уровне групп и permissions и требует финального прикладного сценария.

## Что ещё осталось закрыть
- Перевести публичные данные фильмов, кинотеатров и расписания с hardcoded-структур в `core/views.py` на полную работу через ORM и админку.
- Пройти финальный ручной QA по шаблонам, чтобы исключить остаточные проблемы с вёрсткой и кодировкой.
- Проверить историю коммитов в GitHub и при необходимости сделать более осмысленные тематические коммиты перед защитой.

## Полезные ссылки в проекте
- Главная: `/`
- Фильмы: `/movies/`
- Кинотеатры: `/cinemas/`
- Расписание: `/schedule/`
- Контакты: `/contacts/`
- FAQ: `/faq/`
- Админка: `/admin/`
- ORM-отчёт: `/catalog/report/`

## JS scenarios (21)
1. Переключение темы `dark/light`.
2. Сохранение темы в `localStorage`.
3. Автопрокрутка слайдов на главной.
4. Ручное переключение карусели по dot-кнопкам.
5. Управление каруселью с клавиатуры.
6. Пауза карусели при hover/focus.
7. Автоскрытие Django messages.
8. Ручное закрытие сообщений.
9. Кнопка «Наверх».
10. Показ/скрытие пароля.
11. Tooltip через `title` из `aria-label`.
12. Confirm-диалог для удаления.
13. Защита от двойного submit.
14. Debounce-поиск в каталоге.
15. Сохранение фильтров каталога в `localStorage`.
16. Копирование ссылки на фильм.
17. Live-подсчёт суммы билетов.
18. FAQ accordion с запоминанием.
19. Lazy loading изображений.
20. Reveal-анимация карточек при скролле.
21. Плавная прокрутка к якорям.
