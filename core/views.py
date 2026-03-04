from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.utils.http import url_has_allowed_host_and_scheme

from accounts.models import Profile
from accounts.forms import ProfileForm
from catalog.models import Movie as CatalogMovie
from favorites.models import Favorite
from orders.models import TicketPurchase, TicketPurchaseItem
from reviews.forms import ReviewForm
from reviews.models import Review

from .forms import ContactForm, TicketPurchaseForm

MOVIES = [
    {
        "title": "The Shawshank Redemption",
        "age_rating": "16+",
        "duration": "142 мин",
        "price": "1200 ₸",
        "description": "История банкира, несправедливо осуждённого, и его жизни в тюрьме Шоушенк.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=e4f99ff6e14dad0ae64f9db869638c990580f58f-10415038-images-thumbs&n=13",
    },
    {
        "title": "The Godfather",
        "age_rating": "18+",
        "duration": "175 мин",
        "price": "1500 ₸",
        "description": "Криминальная сага о мафиозной семье Корлеоне.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=88ec413f57b280d51859f562da7c4ff2bc4c7f93-13108625-images-thumbs&n=13",
    },
    {
        "title": "The Dark Knight",
        "age_rating": "16+",
        "duration": "152 мин",
        "price": "1400 ₸",
        "description": "Бэтмен против Джокера в мрачном Готэме.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=79ad879dbe188d2a6e1d33edf65b1e129bcbfad1-5287630-images-thumbs&n=13",
    },
    {
        "title": "Inception",
        "age_rating": "12+",
        "duration": "148 мин",
        "price": "1300 ₸",
        "description": "Команда внедряется в сны, чтобы изменить реальность.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=0e09dd1576663aa5b4c32d9982a3faa95cc6365a-4823985-images-thumbs&n=13",
    },
    {
        "title": "Interstellar",
        "age_rating": "12+",
        "duration": "169 мин",
        "price": "1500 ₸",
        "description": "Путешествие через космос ради спасения человечества.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=4ab7a914d526c729e6a6637b09f77477f46d2f2c-16321481-images-thumbs&n=13",
    },
    {
        "title": "Fight Club",
        "age_rating": "18+",
        "duration": "139 мин",
        "price": "1200 ₸",
        "description": "История подпольного бойцовского клуба и кризиса личности.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=debbc9a0e5217e445fdfb0b823d7ec82e3651a38-5192502-images-thumbs&n=13",
    },
    {
        "title": "Forrest Gump",
        "age_rating": "12+",
        "duration": "142 мин",
        "price": "1100 ₸",
        "description": "Жизнь простого человека на фоне исторических событий США.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=411c8c0adaa41f56fb894b932885e74e8f16e7b4-5221583-images-thumbs&n=13",
    },
    {
        "title": "Titanic",
        "age_rating": "12+",
        "duration": "195 мин",
        "price": "1300 ₸",
        "description": "Любовная история на борту обречённого лайнера.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=1ed40028faf10d00a36f193decd1846a5e494c9b-4936799-images-thumbs&n=13",
    },
    {
        "title": "Gladiator",
        "age_rating": "16+",
        "duration": "155 мин",
        "price": "1300 ₸",
        "description": "Римский генерал становится гладиатором ради мести.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=d1353308a4d558ccd084e03c45f249a885df47f8-6503967-images-thumbs&n=13",
    },
    {
        "title": "The Matrix",
        "age_rating": "16+",
        "duration": "136 мин",
        "price": "1200 ₸",
        "description": "Человек узнаёт, что мир — это компьютерная симуляция.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=c1c21abc87f88236718167fa6ae026c07e0945ba-16325629-images-thumbs&n=13",
    },
    {
        "title": "Avengers: Endgame",
        "age_rating": "12+",
        "duration": "181 мин",
        "price": "1500 ₸",
        "description": "Финальная битва Мстителей против Таноса.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=d8aac44bf80db094458183f117281a1dcb2e353c-5281326-images-thumbs&n=13",
    },
    {
        "title": "Joker",
        "age_rating": "18+",
        "duration": "122 мин",
        "price": "1300 ₸",
        "description": "История становления одного из самых известных злодеев.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=490dea9694af939690f179d31d586d1afb34f88d-10242576-images-thumbs&n=13",
    },
    {
        "title": "Parasite",
        "age_rating": "16+",
        "duration": "132 мин",
        "price": "1200 ₸",
        "description": "Социальная драма о столкновении двух семей.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=013272df7c276e199cd80d7774b9dbca070297d6-5234911-images-thumbs&n=13",
    },
    {
        "title": "The Lion King",
        "age_rating": "6+",
        "duration": "88 мин",
        "price": "1000 ₸",
        "description": "Анимационная история о львёнке Симбе.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=a8a574f8c45e220eda3c977756a1852247396dcf-4451190-images-thumbs&n=13",
    },
    {
        "title": "The Wolf of Wall Street",
        "age_rating": "18+",
        "duration": "180 мин",
        "price": "1500 ₸",
        "description": "История взлёта и падения брокера-миллионера.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=f2372547512505bf92de894aa366bd8ac79a08cb-10701561-images-thumbs&n=13",
    },
    {
        "title": "Django Unchained",
        "age_rating": "18+",
        "duration": "165 мин",
        "price": "1400 ₸",
        "description": "Вестерн о мести и освобождении.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=8f761756909b2e0bebd9376f105a5ec6cc72ffd8-10766948-images-thumbs&n=13",
    },
    {
        "title": "The Lord of the Rings: The Return of the King",
        "age_rating": "12+",
        "duration": "201 мин",
        "price": "1600 ₸",
        "description": "Финальная битва за Средиземье.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=6bda3485a184ae3c1b8390ff91a4e48ec5a11518-8257511-images-thumbs&n=13",
    },
    {
        "title": "Harry Potter and the Sorcerer's Stone",
        "age_rating": "6+",
        "duration": "152 мин",
        "price": "1200 ₸",
        "description": "Начало истории мальчика-волшебника.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=662030c8b8b39b78a7427e50f5aba11dba5d9055-5147227-images-thumbs&n=13",
    },
    {
        "title": "The Avengers",
        "age_rating": "12+",
        "duration": "143 мин",
        "price": "1300 ₸",
        "description": "Супергерои объединяются ради спасения Земли.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=c5371c24a30820b6ba409c23ef35ccec63dac0e9-5233839-images-thumbs&n=13",
    },
    {
        "title": "The Silence of the Lambs",
        "age_rating": "18+",
        "duration": "118 мин",
        "price": "1200 ₸",
        "description": "Агент ФБР охотится на маньяка.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=95a51ed0eda04bfa0e446eaa7abadd309d2e5374-5434068-images-thumbs&n=13",
    },
    {
        "title": "The Green Mile",
        "age_rating": "16+",
        "duration": "189 мин",
        "price": "1400 ₸",
        "description": "Трогательная история о чуде в тюрьме.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=2dac00c469382c6f8eabcd44b201e1062f309c76-7004933-images-thumbs&n=13",
    },
    {
        "title": "Saving Private Ryan",
        "age_rating": "18+",
        "duration": "169 мин",
        "price": "1400 ₸",
        "description": "Военная драма о спасении солдата.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=9eba97dcb6196e3f33ddf514c18298175365896d-4034704-images-thumbs&n=13",
    },
    {
        "title": "The Prestige",
        "age_rating": "12+",
        "duration": "130 мин",
        "price": "1200 ₸",
        "description": "Соперничество двух иллюзионистов.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=ab91df2fd4b9b1561c4485e61ce2578e5915bc3d-12481490-images-thumbs&n=13",
    },
    {
        "title": "The Departed",
        "age_rating": "18+",
        "duration": "151 мин",
        "price": "1300 ₸",
        "description": "Криминальный триллер о двойных агентах.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=a30366a6ab23fda8ade5fb9d274d6d425182b8c3-10303547-images-thumbs&n=13",
    },
    {
        "title": "Whiplash",
        "age_rating": "16+",
        "duration": "106 мин",
        "price": "1100 ₸",
        "description": "История одержимого барабанщика.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=e8f0aa7f9f0e2121ab1cf9c1e1bfff86c91fb762-5524638-images-thumbs&n=13",
    },
    {
        "title": "Top Gun: Maverick",
        "age_rating": "12+",
        "duration": "131 мин",
        "price": "1400 ₸",
        "description": "Продолжение истории пилота-аса.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=9bfabe829e49283a3fd8dd1b39964d879b4bce4c-5232391-images-thumbs&n=13",
    },
    {
        "title": "Oppenheimer",
        "age_rating": "16+",
        "duration": "180 мин",
        "price": "1500 ₸",
        "description": "Биография создателя атомной бомбы.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=68a59e7f2817b9b06218da617c3129037ee7c953-4373887-images-thumbs&n=13",
    },
    {
        "title": "Spider-Man: No Way Home",
        "age_rating": "12+",
        "duration": "148 мин",
        "price": "1400 ₸",
        "description": "Мультивселенная и приключения Человека-паука.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=f5030f94b1ddd397a9112f1dc1af10b28c61e284-4968350-images-thumbs&n=13",
    },
    {
        "title": "The Social Network",
        "age_rating": "12+",
        "duration": "120 мин",
        "price": "1100 ₸",
        "description": "История создания Facebook.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=ca561076c709f44abe03a48838be7c800d5af181-10594781-images-thumbs&n=13",
    },
    {
        "title": "Avatar",
        "age_rating": "12+",
        "duration": "162 мин",
        "price": "1500 ₸",
        "description": "Фантастический мир Пандоры и борьба за природу.",
        "poster_url": "https://avatars.mds.yandex.net/i?id=ae67bda2f4cad16d8ba21ba8e9a0f7ac9e170e14-12605172-images-thumbs&n=13",
    },
]

for movie in MOVIES:
    movie['slug'] = slugify(movie['title'])

MOVIES_BY_TITLE = {movie['title']: movie for movie in MOVIES}
MOVIES_BY_SLUG = {movie['slug']: movie for movie in MOVIES}

HOME_FEATURED_MOVIES = [
    {
        'movie_title': 'The Shawshank Redemption',
        'tag': 'Драма',
    },
    {
        'movie_title': 'The Godfather',
        'tag': 'Криминал',
    },
    {
        'movie_title': 'The Dark Knight',
        'tag': 'Экшен',
    },
]

HOME_CAROUSELS = [
    {
        'title': 'Премьера недели',
        'cta': 'Подробнее',
        'interval_ms': 2600,
        'movie_titles': [
            'Oppenheimer',
            'Spider-Man: No Way Home',
            'Avatar',
            'Top Gun: Maverick',
            'Avengers: Endgame',
        ],
    },
    {
        'title': 'Топ зрителей',
        'cta': 'Подробнее',
        'interval_ms': 3000,
        'movie_titles': [
            'The Shawshank Redemption',
            'The Godfather',
            'The Dark Knight',
            'The Matrix',
            'Interstellar',
            'The Green Mile',
        ],
    },
    {
        'title': 'Рекомендуем сегодня',
        'cta': 'Подробнее',
        'interval_ms': 3400,
        'movie_titles': [
            'Inception',
            'Joker',
            'Parasite',
            'The Prestige',
            'The Departed',
            'Whiplash',
        ],
    },
]

CINEMAS = [
    {
        'slug': 'aport-mall',
        'name': 'CineTicket Aport Mall',
        'address': 'Ташкенский тракт, 17к, Алматы, Молл-Апорт, 2-этаж',
    },
    {
        'slug': 'al-farabi',
        'name': 'CineTicket Al-Farabi',
        'address': 'Республика Казахстан, Алматы, 050040, Аль-Фараби, 77/8, 4-этаж',
    },
    {
        'slug': 'microdistrict-8',
        'name': 'CineTicket 8 мкр.',
        'address': '8-микрорайон, 37/1, 3-этаж, Алматы',
    },
    {
        'slug': 'rozybakiev',
        'name': 'CineTicket Rozybakiev',
        'address': 'Улица Розыбакиева, 247а, 2-этаж, Алматы',
    },
]

CINEMA_BY_SLUG = {cinema['slug']: cinema for cinema in CINEMAS}

CINEMA_SCHEDULES = {
    'aport-mall': [
        {'movie_title': 'The Shawshank Redemption', 'show_time': '11:20', 'start_date': '01.03.2026', 'end_date': '21.03.2026', 'hall': 'Зал 1'},
        {'movie_title': 'The Dark Knight', 'show_time': '13:40', 'start_date': '01.03.2026', 'end_date': '28.03.2026', 'hall': 'Зал 3'},
        {'movie_title': 'Inception', 'show_time': '16:10', 'start_date': '05.03.2026', 'end_date': '25.03.2026', 'hall': 'Зал 2'},
        {'movie_title': 'Interstellar', 'show_time': '18:50', 'start_date': '03.03.2026', 'end_date': '31.03.2026', 'hall': 'IMAX'},
        {'movie_title': 'Avengers: Endgame', 'show_time': '20:30', 'start_date': '02.03.2026', 'end_date': '27.03.2026', 'hall': 'Зал 4'},
        {'movie_title': 'Oppenheimer', 'show_time': '21:10', 'start_date': '01.03.2026', 'end_date': '30.03.2026', 'hall': 'Зал 5'},
        {'movie_title': 'Spider-Man: No Way Home', 'show_time': '14:25', 'start_date': '04.03.2026', 'end_date': '24.03.2026', 'hall': 'Зал 6'},
        {'movie_title': 'Avatar', 'show_time': '19:30', 'start_date': '01.03.2026', 'end_date': '31.03.2026', 'hall': 'Зал 7'},
    ],
    'al-farabi': [
        {'movie_title': 'The Godfather', 'show_time': '12:00', 'start_date': '01.03.2026', 'end_date': '22.03.2026', 'hall': 'Зал 1'},
        {'movie_title': 'Fight Club', 'show_time': '14:45', 'start_date': '06.03.2026', 'end_date': '26.03.2026', 'hall': 'Зал 2'},
        {'movie_title': 'Titanic', 'show_time': '17:40', 'start_date': '01.03.2026', 'end_date': '31.03.2026', 'hall': 'Зал 3'},
        {'movie_title': 'Gladiator', 'show_time': '20:20', 'start_date': '03.03.2026', 'end_date': '28.03.2026', 'hall': 'Зал 4'},
        {'movie_title': 'Joker', 'show_time': '22:10', 'start_date': '02.03.2026', 'end_date': '30.03.2026', 'hall': 'Зал 5'},
        {'movie_title': 'Parasite', 'show_time': '15:30', 'start_date': '08.03.2026', 'end_date': '29.03.2026', 'hall': 'Зал 6'},
        {'movie_title': 'Whiplash', 'show_time': '13:20', 'start_date': '05.03.2026', 'end_date': '27.03.2026', 'hall': 'Зал 7'},
        {'movie_title': 'Top Gun: Maverick', 'show_time': '19:10', 'start_date': '01.03.2026', 'end_date': '31.03.2026', 'hall': 'Зал 8'},
    ],
    'microdistrict-8': [
        {'movie_title': 'Forrest Gump', 'show_time': '10:50', 'start_date': '01.03.2026', 'end_date': '20.03.2026', 'hall': 'Зал 1'},
        {'movie_title': 'The Matrix', 'show_time': '13:05', 'start_date': '02.03.2026', 'end_date': '24.03.2026', 'hall': 'Зал 2'},
        {'movie_title': 'The Lion King', 'show_time': '11:15', 'start_date': '01.03.2026', 'end_date': '31.03.2026', 'hall': 'Зал 3'},
        {'movie_title': "The Lord of the Rings: The Return of the King", 'show_time': '16:40', 'start_date': '04.03.2026', 'end_date': '31.03.2026', 'hall': 'Зал 4'},
        {'movie_title': "Harry Potter and the Sorcerer's Stone", 'show_time': '14:30', 'start_date': '03.03.2026', 'end_date': '28.03.2026', 'hall': 'Зал 5'},
        {'movie_title': 'The Social Network', 'show_time': '18:30', 'start_date': '07.03.2026', 'end_date': '25.03.2026', 'hall': 'Зал 6'},
        {'movie_title': 'The Prestige', 'show_time': '20:00', 'start_date': '01.03.2026', 'end_date': '23.03.2026', 'hall': 'Зал 7'},
        {'movie_title': 'The Avengers', 'show_time': '21:40', 'start_date': '01.03.2026', 'end_date': '31.03.2026', 'hall': 'Зал 8'},
    ],
    'rozybakiev': [
        {'movie_title': 'Django Unchained', 'show_time': '12:30', 'start_date': '01.03.2026', 'end_date': '25.03.2026', 'hall': 'Зал 1'},
        {'movie_title': 'The Departed', 'show_time': '15:15', 'start_date': '06.03.2026', 'end_date': '27.03.2026', 'hall': 'Зал 2'},
        {'movie_title': 'The Silence of the Lambs', 'show_time': '17:05', 'start_date': '01.03.2026', 'end_date': '22.03.2026', 'hall': 'Зал 3'},
        {'movie_title': 'The Green Mile', 'show_time': '19:55', 'start_date': '02.03.2026', 'end_date': '30.03.2026', 'hall': 'Зал 4'},
        {'movie_title': 'Saving Private Ryan', 'show_time': '21:30', 'start_date': '03.03.2026', 'end_date': '31.03.2026', 'hall': 'Зал 5'},
        {'movie_title': 'The Wolf of Wall Street', 'show_time': '16:00', 'start_date': '05.03.2026', 'end_date': '28.03.2026', 'hall': 'Зал 6'},
        {'movie_title': 'Oppenheimer', 'show_time': '13:50', 'start_date': '01.03.2026', 'end_date': '31.03.2026', 'hall': 'Зал 7'},
        {'movie_title': 'Avatar', 'show_time': '20:40', 'start_date': '04.03.2026', 'end_date': '31.03.2026', 'hall': 'Зал 8'},
    ],
}


def _get_home_featured_movies():
    featured = []
    for item in HOME_FEATURED_MOVIES:
        movie = MOVIES_BY_TITLE.get(item['movie_title'])
        if movie:
            featured.append(
                {
                    'tag': item['tag'],
                    'movie': movie,
                }
            )
    return featured


def _get_home_carousels():
    carousels = []
    for index, carousel in enumerate(HOME_CAROUSELS, start=1):
        slides = []
        for movie_title in carousel['movie_titles']:
            movie = MOVIES_BY_TITLE.get(movie_title)
            if movie:
                slides.append(movie)

        if slides:
            carousels.append(
                {
                    'id': f'home-carousel-{index}',
                    'title': carousel['title'],
                    'cta': carousel['cta'],
                    'interval_ms': carousel['interval_ms'],
                    'slides': slides,
                }
            )
    return carousels


def home(request):
    return render(
        request,
        'core/home.html',
        {
            'featured_movies': _get_home_featured_movies(),
            'home_carousels': _get_home_carousels(),
        },
    )


def movies(request):
    favorite_titles = set()
    if request.user.is_authenticated:
        favorite_titles = set(
            Favorite.objects.filter(user=request.user).values_list('movie_title', flat=True)
        )

    search_query = (request.GET.get('q') or '').strip()
    age_filter = (request.GET.get('age') or '').strip()
    age_options = ['6+', '12+', '16+', '18+']

    filtered_movies = MOVIES
    if search_query:
        lower_query = search_query.lower()
        filtered_movies = [movie for movie in filtered_movies if lower_query in movie['title'].lower()]

    if age_filter in age_options:
        filtered_movies = [movie for movie in filtered_movies if movie['age_rating'] == age_filter]

    paginator = Paginator(filtered_movies, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    movie_rating_stats = {
        item["slug"]: {
            "avg_rating": item["avg_rating"],
            "review_count": item["review_count"],
        }
        for item in CatalogMovie.objects.annotate(
            avg_rating=Avg("reviews__rating"),
            review_count=Count("reviews"),
        ).values("slug", "avg_rating", "review_count")
    }

    return render(
        request,
        'core/movies.html',
        {
            'movies': page_obj.object_list,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'ticket_tariffs': TicketPurchase.get_ticket_tariffs(),
            'favorite_titles': favorite_titles,
            'search_query': search_query,
            'age_filter': age_filter,
            'age_options': age_options,
            'movie_rating_stats': movie_rating_stats,
        },
    )


@login_required
def buy_tickets(request):
    movie_title = request.GET.get('movie') if request.method == 'GET' else request.POST.get('movie_title')
    available_titles = set(MOVIES_BY_TITLE.keys())
    ticket_type_map = {
        'adult_qty': TicketPurchase.TICKET_ADULT,
        'student_qty': TicketPurchase.TICKET_STUDENT,
        'child_qty': TicketPurchase.TICKET_CHILD,
    }

    if request.method == 'POST':
        form = TicketPurchaseForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['movie_title']
            if title not in available_titles:
                form.add_error(None, 'Movie not found in catalog.')
            else:
                quantities = {
                    ticket_code: form.cleaned_data[field_name]
                    for field_name, ticket_code in ticket_type_map.items()
                }
                total_qty = sum(quantities.values())

                purchase = TicketPurchase.objects.create(
                    user=request.user,
                    movie_title=title,
                    ticket_type=TicketPurchase.TICKET_ADULT,
                    quantity=max(total_qty, 1),
                    price_per_ticket=0,
                    total_price=0,
                )

                for ticket_type, qty in quantities.items():
                    if qty > 0:
                        TicketPurchaseItem.objects.create(
                            purchase=purchase,
                            ticket_type=ticket_type,
                            quantity=qty,
                            price_per_ticket=0,
                            line_total=0,
                        )

                purchase.recalculate_from_items()
                messages.success(request, 'Purchase completed successfully.')
                return redirect('core:tickets')
    else:
        if not movie_title or movie_title not in available_titles:
            messages.error(request, 'Select movie first from catalog.')
            return redirect('core:movies')
        form = TicketPurchaseForm(
            initial={
                'movie_title': movie_title,
                'adult_qty': 1,
                'student_qty': 0,
                'child_qty': 0,
            }
        )

    return render(
        request,
        'core/buy_tickets.html',
        {
            'form': form,
            'movie_title': movie_title,
            'ticket_tariffs': TicketPurchase.get_ticket_tariffs(),
        },
    )


def schedule(request):
    return render(request, 'core/schedule.html', {'cinemas': CINEMAS})


def cinemas(request):
    return render(request, 'core/cinemas.html', {'cinemas': CINEMAS})


def schedule_cinema(request, cinema_slug):
    cinema = CINEMA_BY_SLUG.get(cinema_slug)
    if not cinema:
        return render(request, 'errors/404.html', status=404)

    sessions = []
    for session in CINEMA_SCHEDULES.get(cinema_slug, []):
        movie = MOVIES_BY_TITLE.get(session['movie_title'])
        if movie:
            sessions.append(
                {
                    **session,
                    'movie': movie,
                }
            )

    return render(
        request,
        'core/schedule.html',
        {
            'cinemas': CINEMAS,
            'selected_cinema': cinema,
            'sessions': sessions,
        },
    )


def movie_detail(request, movie_slug):
    movie = MOVIES_BY_SLUG.get(movie_slug)
    if not movie:
        raise Http404('Movie not found')

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, movie_title=movie['title']).exists()

    db_movie = (
        CatalogMovie.objects.select_related("age_rating")
        .filter(slug=movie_slug)
        .annotate(avg_rating=Avg("reviews__rating"), review_count=Count("reviews"))
        .first()
    )
    avg_rating = db_movie.avg_rating if db_movie else None
    review_count = db_movie.review_count if db_movie else 0

    review_form = None
    user_review = None
    recent_reviews = []

    if db_movie:
        recent_reviews = db_movie.reviews.select_related("user").order_by("-created_at")[:8]
        if request.user.is_authenticated:
            user_review = Review.objects.filter(movie=db_movie, user=request.user).first()
            review_form = ReviewForm(instance=user_review)

    return render(
        request,
        'core/movie_detail.html',
        {
            'movie': movie,
            'ticket_tariffs': TicketPurchase.get_ticket_tariffs(),
            'is_favorite': is_favorite,
            'db_movie': db_movie,
            'avg_rating': avg_rating,
            'review_count': review_count,
            'review_form': review_form,
            'user_review': user_review,
            'recent_reviews': recent_reviews,
        },
    )


@login_required
def tickets(request):
    purchases = TicketPurchase.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'core/tickets.html', {'purchases': purchases})


@login_required
def cancel_ticket(request, purchase_id):
    if request.method != 'POST':
        return redirect('core:tickets')

    purchase = get_object_or_404(TicketPurchase, id=purchase_id, user=request.user)
    purchase.delete()
    messages.success(request, 'Purchase deleted.')
    return redirect('core:tickets')


@login_required
def toggle_favorite(request):
    if request.method != 'POST':
        return redirect('core:movies')

    movie_title = (request.POST.get('movie_title') or '').strip()
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')

    if movie_title not in MOVIES_BY_TITLE:
        messages.error(request, 'Фильм не найден.')
    else:
        favorite, created = Favorite.objects.get_or_create(user=request.user, movie_title=movie_title)
        if created:
            messages.success(request, 'Фильм добавлен в избранное.')
        else:
            favorite.delete()
            messages.info(request, 'Фильм удален из избранного.')

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect('core:movies')


def news(request):
    return render(request, 'core/news.html')


def contacts(request):
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }
        phone_number = getattr(getattr(request.user, 'profile', None), 'phone_number', '')
        if phone_number:
            initial_data['phone'] = phone_number

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            recipient = getattr(settings, 'CONTACT_RECEIVER_EMAIL', 'sabitsaan155@gmail.com')
            subject = f"CineTicket: сообщение от {form.cleaned_data['name']}"
            message_body = (
                f"Имя: {form.cleaned_data['name']}\n"
                f"Email: {form.cleaned_data['email']}\n"
                f"Телефон: {form.cleaned_data.get('phone') or 'не указан'}\n\n"
                f"Сообщение:\n{form.cleaned_data['message']}"
            )

            try:
                send_mail(
                    subject=subject,
                    message=message_body,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', form.cleaned_data['email']),
                    recipient_list=[recipient],
                    fail_silently=False,
                )
            except Exception:
                messages.error(
                    request,
                    'Не удалось отправить сообщение. Проверьте настройки email в .env и попробуйте снова.',
                )
            else:
                messages.success(request, 'Сообщение отправлено. Мы свяжемся с вами в ближайшее время.')
                return redirect('core:contacts')
    else:
        form = ContactForm(initial=initial_data)

    return render(request, 'core/contacts.html', {'form': form})


def faq(request):
    return render(request, 'core/faq.html')


def about(request):
    return render(request, 'core/about.html')


@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен.')
            return redirect('core:profile')
        messages.error(request, 'Не удалось обновить профиль. Проверьте введенные данные.')
    else:
        form = ProfileForm(instance=profile_obj)

    purchases = TicketPurchase.objects.filter(user=request.user).prefetch_related('items')
    return render(
        request,
        'core/profile.html',
        {
            'profile_obj': profile_obj,
            'purchases': purchases,
            'form': form,
        },
    )


@login_required
def favorites(request):
    favorite_records = Favorite.objects.filter(user=request.user).order_by('-created_at')
    favorite_movies = [MOVIES_BY_TITLE[item.movie_title] for item in favorite_records if item.movie_title in MOVIES_BY_TITLE]
    favorite_titles = {movie['title'] for movie in favorite_movies}

    return render(
        request,
        'core/favorites.html',
        {
            'movies': favorite_movies,
            'favorite_titles': favorite_titles,
            'ticket_tariffs': TicketPurchase.get_ticket_tariffs(),
        },
    )


def checkout(request):
    return render(request, 'core/checkout.html')


def hello(request):
    return HttpResponse('Привет, Django!')


def error_404(request, exception):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)
