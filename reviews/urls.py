from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("movie/<slug:movie_slug>/", views.upsert_review, name="upsert"),
    path("movie/<slug:movie_slug>/delete/", views.delete_review, name="delete"),
]
