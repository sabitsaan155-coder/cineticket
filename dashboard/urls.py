from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("manager/", views.manager_dashboard, name="manager"),
]
