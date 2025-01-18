import re
from django.shortcuts import render
from demand.models import Vacancy
from django.db.models import Avg, Count
from django.db.models.functions import Substr


def index(request):
    profession = ['Тестировщик (QA-инженер)', 'Тестировщик', 'QA-инженер', 'qa', 'test', 'тест', 'quality assurance']
    profession_regex = '|'.join(map(re.escape, profession))
    data_get_salary_year_dynamic_prof = (
        Vacancy.objects.exclude(salary__isnull=True)
        .filter(salary__lte=10000000)
        .filter(name__regex=profession_regex)
        .annotate(year=Substr('date', 1, 4))
        .values("year")
        .annotate(avg_salary=Avg("salary"))
        .values("avg_salary", "year")
        .order_by("year")
    )
    data_get_count_year_dynamic_prof = (
        Vacancy.objects.exclude(salary__isnull=True)
        .filter(name__regex=profession_regex)
        .annotate(year=Substr("date", 1, 4))
        .values("year")
        .annotate(count_id=Count("id"))
        .values("count_id", "year")
    )

    context = {
        'get_salary_year_dynamic_prof': {
            'title': "Динамика уровня зарплат по годам для вакансии Тестировщик (QA-инженер)",
            'first_parameter': 'Средняя зарплата вакансии Тестировщик',
            'second_parameter': 'Год',
            'data': [{'first': round(row['avg_salary']) * 1.0, 'second': row['year']} for row in
                     data_get_salary_year_dynamic_prof],
        },
        'data_get_count_year_dynamic_prof': {
            'title': "Динамика количества вакансий по годам для вакансии Тестировщик (QA-инженер)",
            'first_parameter': 'Количество вакансий год',
            'second_parameter': 'Год',
            'data': [{'first': row['count_id'], 'second': row['year']} for row in data_get_count_year_dynamic_prof],
        },
    }
    return render(request, 'demand/index.html', context)