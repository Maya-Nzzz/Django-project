import re

from django.shortcuts import render
from demand.models import Vacancy
from django.db.models import Avg, Count, FloatField, F
from django.db.models.functions import Round


def index(request):
    profession = ['Тестировщик (QA-инженер)', 'Тестировщик', 'QA-инженер', 'qa', 'test', 'тест', 'quality assurance']
    profession_regex = '|'.join(map(re.escape, profession))
    professional_vacancies = Vacancy.objects.filter(name__iregex=profession_regex)
    all_vacancies = professional_vacancies.count()
    data_get_top_10_salary_city_prof = (
        professional_vacancies
        .values('area_name')
        .annotate(
            average_salary=Avg('salary', output_field=FloatField()),
            count=Count('name'),
            percent=(Count('name') * 1.0 / all_vacancies)
        )
        .filter(percent__gte=0.01)
        .order_by('-average_salary', 'area_name')[:10]
    )
    result_data_get_top_10_salary_city_prof = [
        {
            'average_salary': row['average_salary'],
            'area_name': row['area_name']
        }
        for row in data_get_top_10_salary_city_prof
    ]

    amount_vacancies = Vacancy.objects.filter(salary__isnull=False).filter(name__regex=profession_regex).count()
    data_get_top_10_vac_city_prof = (Vacancy
                                     .objects
                                     .filter(name__regex=profession_regex)
                                     .values('area_name')
                                     .filter(salary__isnull=False)
                                     .annotate(count=Count('salary'))
                                     .annotate(percent=Round(F('count') * 1.0 / amount_vacancies, 4))
                                     .filter(percent__gt=0.01)
                                     .order_by('-percent')[:10]
                                     )
    result_data_get_top_10_vac_city_prof = [
        {
            'first': str(row['percent']),
            'second': str(row['area_name'])
        }
        for row in data_get_top_10_vac_city_prof
    ]

    context = {
        'get_top_10_salary_city_prof': {
            'title': "Уровень зарплат по городам для вакансии Тестировщик (QA-инженер)",
            'first_parameter': 'Средняя зарплата',
            'second_parameter': 'Город',
            'data': [{"first": round(row['average_salary']), "second": row['area_name']}
                     for row in result_data_get_top_10_salary_city_prof]},
        'get_top_10_vac_city_prof': {
            'title': "Доля вакансий Тестировщик (QA-инженер) по городам",
            'first_parameter': 'Доля вакансий',
            'second_parameter': 'Город',
            'data': result_data_get_top_10_vac_city_prof,
        },
    }

    return render(request, 'geography/index.html', context)
