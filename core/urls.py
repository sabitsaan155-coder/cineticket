from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('movies/', views.movies, name='movies'),
    path('movies/<slug:movie_slug>/', views.movie_detail, name='movie_detail'),
    path('tickets/buy/', views.buy_tickets, name='buy_tickets'),
    path('schedule/', views.schedule, name='schedule'),
    path('schedule/<slug:cinema_slug>/', views.schedule_cinema, name='schedule_cinema'),
    path('cinemas/', views.cinemas, name='cinemas'),
    path('tickets/', views.tickets, name='tickets'),
    path('tickets/cancel/<int:purchase_id>/', views.cancel_ticket, name='cancel_ticket'),
    path('favorites/toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('news/', views.news, name='news'),
    path('contacts/', views.contacts, name='contacts'),
    path('faq/', views.faq, name='faq'),
    path('about/', views.about, name='about'),
    path('profile/', views.profile, name='profile'),
    path('favorites/', views.favorites, name='favorites'),
    path('checkout/', views.checkout, name='checkout'),
    path('hello/', views.hello, name='hello'),
]
