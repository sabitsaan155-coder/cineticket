from datetime import date, datetime

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils.timezone import make_aware

from catalog.models import (
    AgeRating,
    Amenity,
    Cinema,
    Country,
    FormatType,
    Genre,
    Hall,
    HallAmenity,
    Language,
    Movie,
    MovieCast,
    Person,
    Screening,
    Studio,
    TicketCategory,
    TicketPrice,
)


class Command(BaseCommand):
    help = "Seed cinema ORM data (movies, cinemas, screenings, prices, relations)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding catalog data..."))

        kz, _ = Country.objects.get_or_create(name="Казахстан", slug="kazakhstan")
        us, _ = Country.objects.get_or_create(name="США", slug="usa")
        uk, _ = Country.objects.get_or_create(name="Великобритания", slug="uk")

        ru_lang, _ = Language.objects.get_or_create(name="Русский", code="ru", slug="russian")
        en_lang, _ = Language.objects.get_or_create(name="English", code="en", slug="english")

        age6, _ = AgeRating.objects.get_or_create(code="6+", defaults={"min_age": 6})
        age12, _ = AgeRating.objects.get_or_create(code="12+", defaults={"min_age": 12})
        age16, _ = AgeRating.objects.get_or_create(code="16+", defaults={"min_age": 16})
        age18, _ = AgeRating.objects.get_or_create(code="18+", defaults={"min_age": 18})
        age_map = {"6+": age6, "12+": age12, "16+": age16, "18+": age18}

        fmt_2d, _ = FormatType.objects.get_or_create(name="2D", slug="2d")
        fmt_3d, _ = FormatType.objects.get_or_create(name="3D", slug="3d")
        fmt_imax, _ = FormatType.objects.get_or_create(name="IMAX", slug="imax")

        amenity_vip, _ = Amenity.objects.get_or_create(name="VIP кресла", slug="vip-kresla")
        amenity_bar, _ = Amenity.objects.get_or_create(name="Snack bar", slug="snack-bar")
        amenity_dolby, _ = Amenity.objects.get_or_create(name="Dolby Atmos", slug="dolby-atmos")

        wb, _ = Studio.objects.get_or_create(name="Warner Bros.", slug="warner-bros", defaults={"country": us})
        para, _ = Studio.objects.get_or_create(
            name="Paramount Pictures", slug="paramount-pictures", defaults={"country": us}
        )
        universal, _ = Studio.objects.get_or_create(
            name="Universal Pictures", slug="universal-pictures", defaults={"country": us}
        )

        genres = {}
        for genre_name in [
            "Драма",
            "Криминал",
            "Фантастика",
            "Экшен",
            "Триллер",
            "Приключения",
        ]:
            genres[genre_name], _ = Genre.objects.get_or_create(
                name=genre_name, slug=slugify(genre_name, allow_unicode=True)
            )

        people = {}
        for person_name, country in [
            ("Christopher Nolan", uk),
            ("Morgan Freeman", us),
            ("Marlon Brando", us),
            ("Christian Bale", uk),
            ("Leonardo DiCaprio", us),
            ("Matthew McConaughey", us),
        ]:
            people[person_name], _ = Person.objects.get_or_create(
                slug=slugify(person_name),
                defaults={"full_name": person_name, "country": country},
            )

        cinemas_data = [
            ("aport-mall", "CineTicket Aport Mall", "Ташкенский тракт, 17к, Алматы, Молл-Апорт, 2-этаж"),
            (
                "al-farabi",
                "CineTicket Al-Farabi",
                "Республика Казахстан, Алматы, 050040, Аль-Фараби, 77/8, 4-этаж",
            ),
            ("microdistrict-8", "CineTicket 8 мкр.", "8-микрорайон, 37/1, 3-этаж, Алматы"),
            ("rozybakiev", "CineTicket Rozybakiev", "Улица Розыбакиева, 247а, 2-этаж, Алматы"),
        ]
        cinemas = {}
        for slug, name, address in cinemas_data:
            cinemas[slug], _ = Cinema.objects.get_or_create(
                slug=slug, defaults={"name": name, "address": address, "city": "Алматы"}
            )

        halls = {}
        for cinema_slug, hall_name, capacity, hall_format in [
            ("aport-mall", "Зал 1", 120, fmt_2d),
            ("aport-mall", "Зал 2", 110, fmt_3d),
            ("al-farabi", "Зал 1", 140, fmt_imax),
            ("al-farabi", "Зал 2", 90, fmt_2d),
            ("microdistrict-8", "Зал 1", 80, fmt_2d),
            ("microdistrict-8", "Зал 2", 75, fmt_3d),
            ("rozybakiev", "Зал 1", 95, fmt_2d),
            ("rozybakiev", "Зал 2", 105, fmt_imax),
        ]:
            hall, _ = Hall.objects.get_or_create(
                cinema=cinemas[cinema_slug],
                name=hall_name,
                defaults={"capacity": capacity, "format_type": hall_format},
            )
            if hall.format_type_id is None:
                hall.format_type = hall_format
                hall.capacity = capacity
                hall.save(update_fields=["format_type", "capacity"])
            halls[(cinema_slug, hall_name)] = hall

        for hall_key, amenity in [
            (("aport-mall", "Зал 1"), amenity_bar),
            (("aport-mall", "Зал 2"), amenity_vip),
            (("al-farabi", "Зал 1"), amenity_dolby),
            (("rozybakiev", "Зал 2"), amenity_dolby),
        ]:
            HallAmenity.objects.get_or_create(hall=halls[hall_key], amenity=amenity)

        adult, _ = TicketCategory.objects.get_or_create(code="adult", defaults={"title": "Взрослый"})
        student, _ = TicketCategory.objects.get_or_create(code="student", defaults={"title": "Студент"})
        child, _ = TicketCategory.objects.get_or_create(code="child", defaults={"title": "Детский"})

        movie_data = [
            {
                "title": "The Shawshank Redemption",
                "original_title": "The Shawshank Redemption",
                "description": "История банкира, несправедливо осуждённого, и его жизни в тюрьме Шоушенк.",
                "duration_min": 142,
                "release_year": 1994,
                "status": Movie.Status.NOW,
                "age": "16+",
                "country": us,
                "language": en_lang,
                "studio": wb,
                "poster_url": "https://avatars.mds.yandex.net/i?id=e4f99ff6e14dad0ae64f9db869638c990580f58f-10415038-images-thumbs&n=13",
                "genres": ["Драма"],
                "cast": [("Morgan Freeman", "Ellis Boyd 'Red' Redding", 1)],
            },
            {
                "title": "The Godfather",
                "original_title": "The Godfather",
                "description": "Криминальная сага о мафиозной семье Корлеоне.",
                "duration_min": 175,
                "release_year": 1972,
                "status": Movie.Status.NOW,
                "age": "18+",
                "country": us,
                "language": en_lang,
                "studio": para,
                "poster_url": "https://avatars.mds.yandex.net/i?id=88ec413f57b280d51859f562da7c4ff2bc4c7f93-13108625-images-thumbs&n=13",
                "genres": ["Криминал", "Драма"],
                "cast": [("Marlon Brando", "Don Vito Corleone", 1)],
            },
            {
                "title": "The Dark Knight",
                "original_title": "The Dark Knight",
                "description": "Бэтмен против Джокера в мрачном Готэме.",
                "duration_min": 152,
                "release_year": 2008,
                "status": Movie.Status.NOW,
                "age": "16+",
                "country": us,
                "language": en_lang,
                "studio": wb,
                "poster_url": "https://avatars.mds.yandex.net/i?id=79ad879dbe188d2a6e1d33edf65b1e129bcbfad1-5287630-images-thumbs&n=13",
                "genres": ["Экшен", "Триллер"],
                "cast": [("Christian Bale", "Batman / Bruce Wayne", 1)],
            },
            {
                "title": "Inception",
                "original_title": "Inception",
                "description": "Команда внедряется в сны, чтобы изменить реальность.",
                "duration_min": 148,
                "release_year": 2010,
                "status": Movie.Status.NOW,
                "age": "12+",
                "country": us,
                "language": en_lang,
                "studio": wb,
                "poster_url": "https://avatars.mds.yandex.net/i?id=0e09dd1576663aa5b4c32d9982a3faa95cc6365a-4823985-images-thumbs&n=13",
                "genres": ["Фантастика", "Триллер"],
                "cast": [("Leonardo DiCaprio", "Cobb", 1)],
            },
            {
                "title": "Interstellar",
                "original_title": "Interstellar",
                "description": "Путешествие через космос ради спасения человечества.",
                "duration_min": 169,
                "release_year": 2014,
                "status": Movie.Status.NOW,
                "age": "12+",
                "country": us,
                "language": en_lang,
                "studio": para,
                "poster_url": "https://avatars.mds.yandex.net/i?id=4ab7a914d526c729e6a6637b09f77477f46d2f2c-16321481-images-thumbs&n=13",
                "genres": ["Фантастика", "Приключения"],
                "cast": [("Matthew McConaughey", "Cooper", 1)],
            },
            {
                "title": "Joker",
                "original_title": "Joker",
                "description": "История становления одного из самых известных злодеев.",
                "duration_min": 122,
                "release_year": 2019,
                "status": Movie.Status.NOW,
                "age": "18+",
                "country": us,
                "language": en_lang,
                "studio": wb,
                "poster_url": "https://avatars.mds.yandex.net/i?id=490dea9694af939690f179d31d586d1afb34f88d-10242576-images-thumbs&n=13",
                "genres": ["Драма", "Триллер"],
                "cast": [],
            },
            {
                "title": "Oppenheimer",
                "original_title": "Oppenheimer",
                "description": "Биография создателя атомной бомбы.",
                "duration_min": 180,
                "release_year": 2023,
                "status": Movie.Status.NOW,
                "age": "16+",
                "country": us,
                "language": en_lang,
                "studio": universal,
                "poster_url": "https://avatars.mds.yandex.net/i?id=68a59e7f2817b9b06218da617c3129037ee7c953-4373887-images-thumbs&n=13",
                "genres": ["Драма"],
                "cast": [("Christopher Nolan", "Director", 1)],
            },
            {
                "title": "Avatar",
                "original_title": "Avatar",
                "description": "Фантастический мир Пандоры и борьба за природу.",
                "duration_min": 162,
                "release_year": 2009,
                "status": Movie.Status.SOON,
                "age": "12+",
                "country": us,
                "language": ru_lang,
                "studio": para,
                "poster_url": "https://avatars.mds.yandex.net/i?id=ae67bda2f4cad16d8ba21ba8e9a0f7ac9e170e14-12605172-images-thumbs&n=13",
                "genres": ["Фантастика", "Приключения"],
                "cast": [],
            },
        ]

        movies = {}
        for item in movie_data:
            movie, _ = Movie.objects.update_or_create(
                slug=slugify(item["title"]),
                defaults={
                    "title": item["title"],
                    "original_title": item["original_title"],
                    "description": item["description"],
                    "duration_min": item["duration_min"],
                    "release_year": item["release_year"],
                    "status": item["status"],
                    "age_rating": age_map[item["age"]],
                    "country": item["country"],
                    "language": item["language"],
                    "studio": item["studio"],
                    "poster_url": item["poster_url"],
                },
            )
            movie.genres.set([genres[name] for name in item["genres"]])
            MovieCast.objects.filter(movie=movie).delete()
            for person_name, role_name, position in item["cast"]:
                MovieCast.objects.create(
                    movie=movie,
                    person=people[person_name],
                    role_name=role_name,
                    position=position,
                )
            movies[movie.slug] = movie

            TicketPrice.objects.update_or_create(
                movie=movie, category=adult, defaults={"price": 2000}
            )
            TicketPrice.objects.update_or_create(
                movie=movie, category=student, defaults={"price": 1500}
            )
            TicketPrice.objects.update_or_create(
                movie=movie, category=child, defaults={"price": 1000}
            )

        screenings_data = [
            ("aport-mall", "Зал 1", "the-shawshank-redemption", "2026-03-01 11:20"),
            ("aport-mall", "Зал 2", "inception", "2026-03-01 16:10"),
            ("al-farabi", "Зал 1", "the-godfather", "2026-03-01 12:00"),
            ("al-farabi", "Зал 2", "joker", "2026-03-01 22:10"),
            ("microdistrict-8", "Зал 1", "interstellar", "2026-03-02 18:50"),
            ("microdistrict-8", "Зал 2", "avatar", "2026-03-03 19:30"),
            ("rozybakiev", "Зал 1", "oppenheimer", "2026-03-04 13:50"),
            ("rozybakiev", "Зал 2", "the-dark-knight", "2026-03-05 20:40"),
        ]

        for cinema_slug, hall_name, movie_slug, start_dt in screenings_data:
            hall = halls[(cinema_slug, hall_name)]
            movie = movies[movie_slug]
            start_at = make_aware(datetime.strptime(start_dt, "%Y-%m-%d %H:%M"))
            screening, _ = Screening.objects.update_or_create(
                hall=hall,
                start_at=start_at,
                defaults={
                    "movie": movie,
                    "run_from": date(2026, 3, 1),
                    "run_to": date(2026, 3, 31),
                },
            )
            screening.full_clean()
            screening.save()

        self.stdout.write(self.style.SUCCESS("Catalog seed completed."))
