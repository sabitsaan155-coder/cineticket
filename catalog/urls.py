from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("report/", views.movie_report, name="report"),
]
