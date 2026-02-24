from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('movies/', views.movies, name='movies'),
    path('schedule/', views.schedule, name='schedule'),
    path('cinemas/', views.cinemas, name='cinemas'),
    path('tickets/', views.tickets, name='tickets'),
    path('news/', views.news, name='news'),
    path('contacts/', views.contacts, name='contacts'),
    path('faq/', views.faq, name='faq'),
    path('profile/', views.profile, name='profile'),
    path('favorites/', views.favorites, name='favorites'),
    path('checkout/', views.checkout, name='checkout'),
    path('hello/', views.hello, name='hello'),
]
