from collections import Counter

import pandas as pd
from django.db.models import Count, Avg, F
from django.db.models.functions import Substr, Round
from django.shortcuts import render
from demand.models import Vacancy
from get_charts import clean_value
from import_csv import get_salary


def declension(number, word):
    if 10 <= number % 100 <= 20:
        return f"{number} {word[2]}"
    if number % 10 == 1:
        return f"{number} {word[0]}"
    if 2 <= number % 10 <= 4:
        return f"{number} {word[1]}"
    return f"{number} {word[2]}"


def index(request):
    data_get_salary_year_dynamic = (
        Vacancy.objects.exclude(salary__isnull=True)
        .filter(salary__lte=10000000)
        .annotate(year=Substr('date', 1, 4))
        .values("year")
        .annotate(avg_salary=Avg("salary"))
        .values("avg_salary", "year")
        .order_by("year")
    )

    data_get_count_year_dynamic = (
        Vacancy.objects.exclude(salary__isnull=True)
        .annotate(year=Substr("date", 1, 4))
        .values("year")
        .annotate(count_id=Count("id"))
        .values("count_id", "year")
    )

    df_currency = pd.read_csv('currency.csv', index_col='date')
    vacancies = pd.read_csv("vacancies_2024.csv", low_memory=False)
    vacancies['date'] = pd.to_datetime(vacancies['published_at'], errors='coerce', utc=True).dt.strftime('%Y-%m')
    vacancies["year"] = pd.to_datetime(vacancies["published_at"], format="%Y-%m-%dT%H:%M:%S%z", utc=True).dt.year
    vacancies["average"] = vacancies.apply(lambda row: get_salary(row, df_currency), axis=1)
    all_vacancies = len(vacancies)
    data_get_top_10_salary_city = (
        vacancies.groupby("area_name")
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

    amount_vacancies = Vacancy.objects.filter(salary__isnull=False).count()
    data_get_top_10_vac_city = (Vacancy
                                .objects
                                .values('area_name')
                                .filter(salary__isnull=False)
                                .annotate(count=Count('salary'))
                                .annotate(percent=Round(F('count') * 1.0 / amount_vacancies, 4))
                                .filter(percent__gt=0.01)
                                .order_by('-percent')[:10]
                                )
    result_data_get_top_10_vac_city = [
        {
            'first': str(row['percent']),
            'second': str(row['area_name'])
        }
        for row in data_get_top_10_vac_city
    ]

    data_get_top_20_skills = (Vacancy
                              .objects
                              .filter(key_skills__isnull=False)
                              .values('key_skills')
                              )
    skills = []
    for skill in data_get_top_20_skills:
        skill = clean_value(skill['key_skills'])
        if isinstance(skill, list):
            skills.extend(skill)
        else:
            skills.append(skill)
    result_data_get_top_20_skills = [
        {
            'first': f"{declension(row[1], ['раз', 'раза', 'раз'])}",
            'second': str(row[0])
        }
        for row in dict(Counter(skills).most_common(20)).items()
    ]

    context = {
        'get_count_year_dynamic': {
            'title': "Динамика количества вакансий по годам",
            'first_parameter': 'Количество вакансий год',
            'second_parameter': 'Год',
            'data': [{'first': row['count_id'], 'second': row['year']} for row in data_get_count_year_dynamic],
        },
        'get_salary_year_dynamic': {
            'title': "Динамика уровня зарплат по годам",
            'first_parameter': 'Средняя зарплата',
            'second_parameter': 'Год',
            'data': [{'first': round(row['avg_salary']) * 1.0, 'second': row['year']} for row in
                     data_get_salary_year_dynamic],
        },
        'get_top_10_salary_city': {
            'title': "Уровень зарплат по городам",
            'first_parameter': 'Средняя зарплата',
            'second_parameter': 'Город',
            'data': [{"first": round(row[1]) * 1.0, "second": row[0]} for row in
                     data_get_top_10_salary_city.items()],
        },
        'get_top_10_vac_city': {
            'title': "Доля вакансий по городам",
            'first_parameter': 'Доля вакансий',
            'second_parameter': 'Город',
            'data': result_data_get_top_10_vac_city,
        },
        'data_get_top_20_skills': {
            'title': f"Из {declension(len(set(skills)), ['скилла', 'скиллов', 'скиллов'])}, самыми популярными являются:",
            'first_parameter': 'Количество',
            'second_parameter': 'Навык',
            'data': result_data_get_top_20_skills,
        }
    }



    return render(request, 'general_statistics/index.html', context)
