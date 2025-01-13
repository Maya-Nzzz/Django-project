from django.shortcuts import render

from demand.models import Vacancy


def index(request):
    vacancies_list = Vacancy.objects.all()
    context = {
        "vacancies_list": vacancies_list[:10],
    }
    return render(request, 'general_statistics/index.html', context)
