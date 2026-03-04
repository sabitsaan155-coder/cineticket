from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from catalog.models import Cinema, Movie, Screening
from reviews.models import Review

from .permissions import user_is_manager


@login_required
def manager_dashboard(request):
    if not user_is_manager(request.user):
        messages.error(request, "Доступ в раздел manager разрешен только роли manager или admin.")
        return redirect("core:home")

    now = timezone.now()
    upcoming_screenings = Screening.objects.filter(start_at__gte=now)

    stats = {
        "movies_total": Movie.objects.count(),
        "movies_now": Movie.objects.filter(status=Movie.Status.NOW).count(),
        "movies_soon": Movie.objects.filter(status=Movie.Status.SOON).count(),
        "cinemas_total": Cinema.objects.count(),
        "screenings_upcoming": upcoming_screenings.count(),
        "reviews_total": Review.objects.count(),
    }

    movies_without_prices = (
        Movie.objects.annotate(price_count=Count("ticket_prices", distinct=True))
        .filter(price_count=0)
        .order_by("title")[:6]
    )

    overloaded_cinemas = (
        Cinema.objects.annotate(
            screening_count=Count("halls__screenings", distinct=True),
            movie_count=Count("halls__screenings__movie", distinct=True),
        )
        .order_by("-screening_count", "name")[:4]
    )

    recent_screenings = (
        Screening.objects.select_related("movie", "hall", "hall__cinema")
        .order_by("start_at")[:8]
    )

    low_review_movies = (
        Movie.objects.annotate(
            review_count=Count("reviews", distinct=True),
            low_scores=Count("reviews", filter=Q(reviews__rating__lte=3), distinct=True),
        )
        .filter(review_count__gt=0)
        .order_by("-low_scores", "title")[:5]
    )

    admin_links = {
        "movies": reverse("admin:catalog_movie_changelist"),
        "screenings": reverse("admin:catalog_screening_changelist"),
        "cinemas": reverse("admin:catalog_cinema_changelist"),
        "prices": reverse("admin:catalog_ticketprice_changelist"),
        "report": reverse("catalog:report"),
    }

    return render(
        request,
        "dashboard/manager.html",
        {
            "stats": stats,
            "movies_without_prices": movies_without_prices,
            "overloaded_cinemas": overloaded_cinemas,
            "recent_screenings": recent_screenings,
            "low_review_movies": low_review_movies,
            "admin_links": admin_links,
        },
    )
