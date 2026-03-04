import json
from datetime import datetime

from django.http import JsonResponse
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt

from catalog.models import AgeRating, Cinema, Country, Genre, Hall, Language, Movie, Screening, Studio


def _api_error(status, code, message, details=None):
    payload = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return JsonResponse(payload, status=status)


def _parse_json_body(request):
    try:
        raw = request.body.decode("utf-8") if request.body else "{}"
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _require_staff(request):
    if not request.user.is_authenticated:
        return _api_error(403, "forbidden", "Authentication required.")
    if not request.user.is_staff:
        return _api_error(403, "forbidden", "Staff permissions required.")
    return None


def _serialize_movie(movie):
    return {
        "id": movie.id,
        "slug": movie.slug,
        "title": movie.title,
        "original_title": movie.original_title,
        "description": movie.description,
        "poster_url": movie.poster_url,
        "duration_min": movie.duration_min,
        "release_year": movie.release_year,
        "status": movie.status,
        "age_rating": movie.age_rating.code if movie.age_rating_id else None,
        "country": movie.country.name if movie.country_id else None,
        "language": movie.language.code if movie.language_id else None,
        "studio": movie.studio.name if movie.studio_id else None,
        "genres": [genre.slug for genre in movie.genres.all()],
    }


def _serialize_cinema(cinema):
    return {
        "id": cinema.id,
        "slug": cinema.slug,
        "name": cinema.name,
        "city": cinema.city,
        "address": cinema.address,
        "halls": [
            {
                "id": hall.id,
                "name": hall.name,
                "capacity": hall.capacity,
                "format": hall.format_type.name if hall.format_type_id else None,
            }
            for hall in cinema.halls.all()
        ],
    }


def _serialize_screening(screening):
    return {
        "id": screening.id,
        "movie": screening.movie.slug,
        "cinema": screening.hall.cinema.slug,
        "hall": screening.hall.name,
        "start_at": timezone.localtime(screening.start_at).isoformat(),
        "run_from": screening.run_from.isoformat(),
        "run_to": screening.run_to.isoformat(),
    }


def _movie_queryset():
    return Movie.objects.select_related("age_rating", "country", "language", "studio").prefetch_related(
        "genres"
    )


@csrf_exempt
def movies_api(request):
    if request.method == "GET":
        queryset = _movie_queryset()

        search = (request.GET.get("search") or "").strip()
        genre = (request.GET.get("genre") or "").strip()
        age_rating = (request.GET.get("age_rating") or "").strip()
        ordering = (request.GET.get("ordering") or "").strip()
        limit = request.GET.get("limit")
        offset = request.GET.get("offset")

        if search:
            queryset = queryset.filter(title__icontains=search)
        if genre:
            queryset = queryset.filter(genres__slug=genre)
        if age_rating:
            queryset = queryset.filter(age_rating__code=age_rating)

        allowed_ordering = {
            "title",
            "-title",
            "release_year",
            "-release_year",
            "duration_min",
            "-duration_min",
        }
        if ordering:
            if ordering not in allowed_ordering:
                return _api_error(400, "bad_request", "Invalid ordering parameter.")
            queryset = queryset.order_by(ordering)

        total = queryset.distinct().count()
        queryset = queryset.distinct()

        if offset is not None:
            try:
                offset_value = int(offset)
                if offset_value < 0:
                    raise ValueError
            except ValueError:
                return _api_error(400, "bad_request", "offset must be a non-negative integer.")
            queryset = queryset[offset_value:]

        if limit is not None:
            try:
                limit_value = int(limit)
                if limit_value <= 0:
                    raise ValueError
            except ValueError:
                return _api_error(400, "bad_request", "limit must be a positive integer.")
            queryset = queryset[:limit_value]

        data = [_serialize_movie(movie) for movie in queryset]
        return JsonResponse({"count": total, "results": data}, status=200)

    if request.method == "POST":
        permission_error = _require_staff(request)
        if permission_error:
            return permission_error

        payload = _parse_json_body(request)
        if payload is None:
            return _api_error(400, "bad_request", "Invalid JSON body.")

        required_fields = ["title", "description", "duration_min", "release_year", "age_rating"]
        missing = [field for field in required_fields if not payload.get(field)]
        if missing:
            return _api_error(400, "bad_request", "Missing required fields.", {"fields": missing})

        slug = payload.get("slug") or slugify(payload["title"])
        if Movie.objects.filter(slug=slug).exists():
            return _api_error(400, "bad_request", "Movie with this slug already exists.")

        try:
            age_rating = AgeRating.objects.get(code=payload["age_rating"])
        except AgeRating.DoesNotExist:
            return _api_error(400, "bad_request", "Unknown age_rating code.")

        movie = Movie(
            title=payload["title"],
            slug=slug,
            original_title=payload.get("original_title", ""),
            description=payload["description"],
            poster_url=payload.get("poster_url", ""),
            duration_min=payload["duration_min"],
            release_year=payload["release_year"],
            status=payload.get("status", Movie.Status.NOW),
            age_rating=age_rating,
        )

        if payload.get("country"):
            movie.country = Country.objects.filter(slug=payload["country"]).first()
        if payload.get("language"):
            movie.language = Language.objects.filter(slug=payload["language"]).first()
        if payload.get("studio"):
            movie.studio = Studio.objects.filter(slug=payload["studio"]).first()

        try:
            movie.full_clean()
        except Exception as exc:  # noqa: BLE001
            return _api_error(400, "bad_request", "Validation error.", {"details": str(exc)})

        movie.save()
        if payload.get("genres"):
            genres = Genre.objects.filter(slug__in=payload["genres"])
            movie.genres.set(genres)

        return JsonResponse(_serialize_movie(movie), status=201)

    return _api_error(400, "bad_request", "Method not supported.")


@csrf_exempt
def movie_detail_api(request, movie_slug):
    movie = _movie_queryset().filter(slug=movie_slug).first()
    if not movie:
        return _api_error(404, "not_found", "Movie not found.")

    if request.method == "GET":
        return JsonResponse(_serialize_movie(movie), status=200)

    if request.method in {"PUT", "PATCH"}:
        permission_error = _require_staff(request)
        if permission_error:
            return permission_error

        payload = _parse_json_body(request)
        if payload is None:
            return _api_error(400, "bad_request", "Invalid JSON body.")

        updatable_fields = [
            "title",
            "original_title",
            "description",
            "poster_url",
            "duration_min",
            "release_year",
            "status",
        ]
        for field in updatable_fields:
            if field in payload:
                setattr(movie, field, payload[field])

        if "age_rating" in payload:
            age_rating = AgeRating.objects.filter(code=payload["age_rating"]).first()
            if not age_rating:
                return _api_error(400, "bad_request", "Unknown age_rating code.")
            movie.age_rating = age_rating

        if "genres" in payload:
            genres = Genre.objects.filter(slug__in=payload["genres"])
            movie.genres.set(genres)

        if "slug" in payload:
            movie.slug = payload["slug"]

        try:
            movie.full_clean()
        except Exception as exc:  # noqa: BLE001
            return _api_error(400, "bad_request", "Validation error.", {"details": str(exc)})

        movie.save()
        return JsonResponse(_serialize_movie(movie), status=200)

    if request.method == "DELETE":
        permission_error = _require_staff(request)
        if permission_error:
            return permission_error
        movie.delete()
        return JsonResponse({"ok": True}, status=200)

    return _api_error(400, "bad_request", "Method not supported.")


def cinemas_api(request):
    if request.method != "GET":
        return _api_error(400, "bad_request", "Method not supported.")

    cinemas = Cinema.objects.prefetch_related("halls__format_type").order_by("name")
    return JsonResponse({"count": cinemas.count(), "results": [_serialize_cinema(c) for c in cinemas]}, status=200)


def cinema_detail_api(request, cinema_slug):
    if request.method != "GET":
        return _api_error(400, "bad_request", "Method not supported.")

    cinema = Cinema.objects.prefetch_related("halls__format_type").filter(slug=cinema_slug).first()
    if not cinema:
        return _api_error(404, "not_found", "Cinema not found.")
    return JsonResponse(_serialize_cinema(cinema), status=200)


def screenings_api(request):
    if request.method != "GET":
        return _api_error(400, "bad_request", "Method not supported.")

    screenings = Screening.objects.select_related("movie", "hall", "hall__cinema").order_by("start_at")
    cinema = (request.GET.get("cinema") or "").strip()
    date_value = (request.GET.get("date") or "").strip()
    date_from = (request.GET.get("date_from") or "").strip()
    date_to = (request.GET.get("date_to") or "").strip()

    if cinema:
        screenings = screenings.filter(hall__cinema__slug=cinema)

    if date_value:
        try:
            parsed = datetime.strptime(date_value, "%Y-%m-%d").date()
        except ValueError:
            return _api_error(400, "bad_request", "date must be YYYY-MM-DD.")
        screenings = screenings.filter(start_at__date=parsed)

    if date_from:
        try:
            parsed_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        except ValueError:
            return _api_error(400, "bad_request", "date_from must be YYYY-MM-DD.")
        screenings = screenings.filter(start_at__date__gte=parsed_from)

    if date_to:
        try:
            parsed_to = datetime.strptime(date_to, "%Y-%m-%d").date()
        except ValueError:
            return _api_error(400, "bad_request", "date_to must be YYYY-MM-DD.")
        screenings = screenings.filter(start_at__date__lte=parsed_to)

    return JsonResponse(
        {"count": screenings.count(), "results": [_serialize_screening(item) for item in screenings]}, status=200
    )


def screening_detail_api(request, screening_id):
    if request.method != "GET":
        return _api_error(400, "bad_request", "Method not supported.")

    screening = (
        Screening.objects.select_related("movie", "hall", "hall__cinema")
        .filter(id=screening_id)
        .first()
    )
    if not screening:
        return _api_error(404, "not_found", "Screening not found.")
    return JsonResponse(_serialize_screening(screening), status=200)


def genres_api(request):
    if request.method != "GET":
        return _api_error(400, "bad_request", "Method not supported.")

    genres = Genre.objects.order_by("name")
    data = [{"id": genre.id, "name": genre.name, "slug": genre.slug} for genre in genres]
    return JsonResponse({"count": len(data), "results": data}, status=200)
