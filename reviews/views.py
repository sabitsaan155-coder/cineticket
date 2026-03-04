from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from catalog.models import Movie

from .forms import ReviewForm
from .models import Review


@login_required
def upsert_review(request, movie_slug):
    if request.method != "POST":
        return redirect("core:movie_detail", movie_slug=movie_slug)

    movie = get_object_or_404(Movie, slug=movie_slug)
    review = Review.objects.filter(movie=movie, user=request.user).first()

    form = ReviewForm(request.POST, instance=review)
    if form.is_valid():
        saved = form.save(commit=False)
        saved.movie = movie
        saved.user = request.user
        saved.save()
        messages.success(request, "Отзыв сохранён.")
    else:
        messages.error(request, "Проверьте рейтинг (1-5) и текст отзыва.")

    return redirect("core:movie_detail", movie_slug=movie_slug)


@login_required
def delete_review(request, movie_slug):
    if request.method != "POST":
        return redirect("core:movie_detail", movie_slug=movie_slug)

    movie = get_object_or_404(Movie, slug=movie_slug)
    review = Review.objects.filter(movie=movie, user=request.user).first()
    if review:
        review.delete()
        messages.success(request, "Ваш отзыв удалён.")
    else:
        messages.info(request, "Отзыв не найден.")

    return redirect("core:movie_detail", movie_slug=movie_slug)
