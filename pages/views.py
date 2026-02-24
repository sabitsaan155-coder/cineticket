from django.shortcuts import render


def about(request):
    return render(request, 'pages/about.html')


def team(request):
    return render(request, 'pages/team.html')
