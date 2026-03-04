from django.db.models import Count
from django.shortcuts import render

from .models import Cinema, Genre, Movie, Screening


def movie_report(request):
    """
    ORM demo report:
    - annotate/Count for statistics
    - select_related/prefetch_related for query optimization
    """
    movies = (
        Movie.objects.select_related("country", "language", "age_rating")
        .prefetch_related("genres")
        .order_by("title")
    )

    screenings = (
        Screening.objects.select_related("movie", "hall", "hall__cinema", "hall__format_type")
        .order_by("start_at")[:20]
    )

    genre_stats = Genre.objects.annotate(movie_count=Count("movies", distinct=True)).order_by(
        "-movie_count", "name"
    )
    cinema_stats = Cinema.objects.annotate(
        hall_count=Count("halls", distinct=True),
        movie_count=Count("halls__screenings__movie", distinct=True),
        screening_count=Count("halls__screenings", distinct=True),
    ).order_by("-screening_count", "name")

    return render(
        request,
        "catalog/report.html",
        {
            "movies": movies,
            "screenings": screenings,
            "genre_stats": genre_stats,
            "cinema_stats": cinema_stats,
        },
    )
