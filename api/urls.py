from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("movies/", views.movies_api, name="movies"),
    path("movies/<slug:movie_slug>/", views.movie_detail_api, name="movie_detail"),
    path("cinemas/", views.cinemas_api, name="cinemas"),
    path("cinemas/<slug:cinema_slug>/", views.cinema_detail_api, name="cinema_detail"),
    path("screenings/", views.screenings_api, name="screenings"),
    path("screenings/<int:screening_id>/", views.screening_detail_api, name="screening_detail"),
    path("genres/", views.genres_api, name="genres"),
]
