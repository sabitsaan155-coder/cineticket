from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    return render(request, 'core/home.html')


def movies(request):
    return render(request, 'core/movies.html')


def schedule(request):
    return render(request, 'core/schedule.html')


def cinemas(request):
    return render(request, 'core/cinemas.html')


def tickets(request):
    return render(request, 'core/tickets.html')


def news(request):
    return render(request, 'core/news.html')


def contacts(request):
    return render(request, 'core/contacts.html')


def faq(request):
    return render(request, 'core/faq.html')


def profile(request):
    return render(request, 'core/profile.html')


def favorites(request):
    return render(request, 'core/favorites.html')


def checkout(request):
    return render(request, 'core/checkout.html')


def hello(request):
    return HttpResponse('Привет, Django!')


def error_404(request, exception):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)
