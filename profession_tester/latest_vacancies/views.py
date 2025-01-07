from django.shortcuts import render


def index(request):
    return render(request, 'latest_vacancies/index.html', {})