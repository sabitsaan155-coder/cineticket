# CineTicket

CineTicket — учебный Django-проект онлайн-киноафиши и покупки билетов.

Проект включает:
- каталог фильмов;
- детальные страницы фильмов;
- расписание по кинотеатрам;
- покупку билетов;
- избранное;
- отзывы и рейтинг;
- профиль пользователя с аватаром;
- Django admin;
- JSON API.

## Что реализовано
- Регистрация, вход, выход и профиль пользователя.
- Загрузка аватара с валидацией размера и типа файла.
- Смена пароля и восстановление пароля через стандартные Django auth views.
- Каталог фильмов с фильтрами, поиском и пагинацией.
- Детальная страница фильма.
- Покупка билетов, включая семейную покупку с несколькими типами билетов в одном заказе.
- История покупок в профиле и отдельный раздел `Билеты`.
- Избранное для авторизованных пользователей.
- Отзывы и рейтинг 1–5, средний рейтинг и количество отзывов.
- Разделы: главная, фильмы, расписание, кинотеатры, контакты, FAQ, о проекте.
- Форма обратной связи на странице контактов.
- Кастомный template tag для сохранения querystring при пагинации.
- Кастомные страницы ошибок 404/500.
- JSON API для фильмов, кинотеатров, сеансов и жанров.
- Расширенная Django admin: `list_display`, `search_fields`, `list_filter`, inline, actions, fieldsets, `prepopulated_fields`, `readonly_fields`.
- Отдельная прикладная роль `manager` через Django Groups / Permissions и `Manager Dashboard`.
- 21 JS-сценарий для UX и интерактивности.
- Seed-команда для заполнения базы фильмов, кинотеатров, тарифов и сеансов.

## Архитектура проекта
Приложения проекта:
- `accounts`
- `api`
- `catalog`
- `core`
- `dashboard`
- `favorites`
- `orders`
- `pages`
- `rentals`
- `reviews`
- `search`

Проект использует единый `base.html`, общий navbar/footer, Django templates, `static/`, `media/` и разделение по приложениям.

## Stack
- Python 3.12+
- Django 5
- SQLite — локальная разработка
- PostgreSQL — прод-конфигурация
- WhiteNoise
- Gunicorn
- Pillow
- Black
- Ruff

## Design Source

This project is based on the free HTML template:

Start Bootstrap - Modern Business  
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
- dark theme overrides in `static/css/main.css`
- page components, forms, cards, catalog, profile, tickets, reviews and JS scenarios

## Запуск локально (Windows PowerShell)
1. Создать и активировать виртуальное окружение:
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

4. Применить миграции:
```powershell
python manage.py migrate
```

5. Заполнить тестовые данные:
```powershell
python manage.py seed_cinema
```

6. Создать суперпользователя:
```powershell
python manage.py createsuperuser
```

7. Запустить сервер:
```powershell
python manage.py runserver
```

## Основные URL
- Главная: `/`
- Фильмы: `/movies/`
- Кинотеатры: `/cinemas/`
- Расписание: `/schedule/`
- Контакты: `/contacts/`
- FAQ: `/faq/`
- Профиль: `/profile/`
- Билеты: `/tickets/`
- Избранное: `/favorites/`
- Manager Dashboard: `/dashboard/manager/`
- Админка: `/admin/`
- ORM-отчет: `/catalog/report/`
- API: `/api/`

## Seed-данные
Команда:
```powershell
python manage.py seed_cinema
```

После выполнения команда создаёт и обновляет:
- 30 фильмов;
- 4 кинотеатра;
- залы и тарифы билетов;
- сеансы для расписания.

## Пользователи и роли
- `user` — регистрация, вход, профиль, покупки, избранное, отзывы.
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

### Защищенные методы
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

## MEDIA / STATIC
- `MEDIA_ROOT` и `MEDIA_URL` настроены.
- В локальном режиме при `DEBUG=True` медиа раздаются через Django.
- `STATIC_ROOT` и `collectstatic` предусмотрены для прод-конфигурации.

Команда:
```powershell
python manage.py collectstatic
```

## Logs
- Локально лог приложения пишется в `logs/django.log`.
- Просмотр в PowerShell:
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
  - ежедневный `pg_dump`;
  - хранение нескольких последних backup-файлов;
  - отдельное хранение резервных копий вне директории проекта.

Пример backup:
```bash
pg_dump -U <db_user> -h <db_host> -Fc <db_name> > backup.dump
```

Пример восстановления:
```bash
pg_restore -U <db_user> -d <db_name> backup.dump
```

## Линтинг и форматирование
Ruff:
```powershell
ruff check .
```

Black:
```powershell
black --check .
```

## Чеклист соответствия требованиям
- [x] 10+ Django apps
- [x] Базовый layout (`base.html`) + активное меню
- [x] Пользователи: регистрация / логин / логаут
- [x] Профиль пользователя, аватар и история покупок
- [x] Пользователи и права доступа (`user`, `staff`, `admin`)
- [x] Отдельная прикладная роль `manager` реализована: доступ через Django Groups / Permissions и отдельный пользовательский сценарий через Manager Dashboard
- [x] Кастомные страницы 404/500
- [x] `.env.example`, `requirements.txt`, `.gitignore`
- [x] MEDIA/STATIC настроены, `collectstatic` предусмотрен
- [x] Пагинация и фильтры в каталоге
- [x] Полноценный API (5+ endpoints)
- [x] Расширенная админка по основным критериям
- [x] Password reset flow
- [x] Reviews + rating + average
- [x] 21 JS scenarios
- [x] Публичные данные фильмов, кинотеатров и расписания работают через ORM и seed-команду

## Текущий статус README
- README синхронизирован с текущим кодом проекта.
- Разделы `Logs`, `Restart (local)`, `Backup strategy`, `API`, `Admin`, `Password reset`, `Avatar upload` и `JS scenarios` актуализированы.
- Формулировки по ролям уточнены: полностью реализованы `user`, `manager`, `admin`.
- Публичные данные фильмов, кинотеатров и расписания переведены на ORM и seed-команду.
- Документация приведена к финальному состоянию перед защитой.

## Финальный статус
- Все основные требования локальной части проекта реализованы.
- Проект готов к демонстрации и защите.

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
17. Live-подсчет суммы билетов.
18. FAQ accordion с запоминанием.
19. Lazy loading изображений.
20. Reveal-анимация карточек при скролле.
21. Плавная прокрутка к якорям.
