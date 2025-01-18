import re

import pandas as pd
from django.shortcuts import render
from demand.models import Vacancy
from django.db.models import Avg, Count, F
from django.db.models.functions import Round

from import_csv import get_salary


def index(request):
    df_currency = pd.read_csv('currency.csv', index_col='date')
    vacancies = pd.read_csv("vacancies_2024.csv", low_memory=False)
    vacancies['date'] = pd.to_datetime(vacancies['published_at'], errors='coerce', utc=True).dt.strftime('%Y-%m')
    vacancies["year"] = pd.to_datetime(vacancies["published_at"], format="%Y-%m-%dT%H:%M:%S%z", utc=True).dt.year
    vacancies["average"] = vacancies.apply(lambda row: get_salary(row, df_currency), axis=1)
    profession = ['Тестировщик (QA-инженер)', 'Тестировщик', 'QA-инженер', 'qa', 'test', 'тест', 'quality assurance']
    profession_regex = '|'.join(map(re.escape, profession))
    professional_vacancies = vacancies[vacancies["name"].str.contains(profession_regex, case=False, na=False)]
    all_vacancies = len(professional_vacancies)
    data_get_top_10_salary_city_prof = (
        professional_vacancies.groupby("area_name")
        .agg(
            average_salary=("average", "mean"),
            count=("name", "count")
        )
        .fillna(0)
        .assign(percent=lambda df: df["count"] / all_vacancies)
        .sort_values(["average_salary", "area_name"], ascending=[False, True])
        .query("percent >= 0.01")
        .reset_index()
        .set_index("area_name")["average_salary"].iloc[:10].to_dict()
    )

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
            'data': [{"first": round(row[1]) * 1.0, "second": row[0]} for row in
                     data_get_top_10_salary_city_prof.items()],
        },
        'get_top_10_vac_city_prof': {
            'title': "Доля вакансий Тестировщик (QA-инженер) по городам",
            'first_parameter': 'Доля вакансий',
            'second_parameter': 'Город',
            'data': result_data_get_top_10_vac_city_prof,
        },
    }
    return render(request, 'geography/index.html', context)
