from django.db.models import Count, Avg, F
from django.db.models.functions import Substr, Round
from django.shortcuts import render
from demand.models import Vacancy


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
        .annotate(year=Substr('published_at', 1, 4))
        .values("year")
        .annotate(count_id=Count("id"))
        .values("count_id", "year")
    )

    data_get_top_10_salary_city = (Vacancy
            .objects
            .exclude(salary__isnull=True)
            .values("area_name")
            .annotate(avg_salary=Avg("salary"), total_vacancies=Count("id"))
            .filter(total_vacancies__gt=1)
            .order_by("avg_salary")
            .values("avg_salary", "area_name"))[:10]

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

    context = {
        'get_count_year_dynamic': {
            'first_parameter': 'Vacancies count',
            'second_parameter': 'Year',
            'data': [{'first': row['count_id'], 'second': row['year']} for row in data_get_count_year_dynamic],
        },
        'get_salary_year_dynamic': {
            'first_parameter': 'Avg salary',
            'second_parameter': 'Year',
            'data': [{'first': round(row['avg_salary']) * 1.0, 'second': row['year']} for row in
                     data_get_salary_year_dynamic],
        },
        'get_top_10_salary_city': {
            'first_parameter': 'Avg salary',
            'second_parameter': 'City',
            'data': [{"first": round(row["avg_salary"]) * 1.0, "second": row["area_name"]} for row in data_get_top_10_salary_city],
        },
        'get_top_10_vac_city': {
            'first_parameter': 'Vacancy rate',
            'second_parameter': 'City',
            'data': result_data_get_top_10_vac_city,
        },
    }

    return render(request, 'general_statistics/index.html', context)
