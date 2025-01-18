from django.shortcuts import render
import requests
import datetime


def index(request):
    vacancies = get_vacancies()
    for vacancy in vacancies:
        vacancy['key_skills'] = ', '.join(vacancy['key_skills'])

        salary = vacancy['salary']
        if salary == {} or (salary['from'] == None and salary['to'] == None):
            salary['message'] = ' - '
        else:
            if salary['to'] != None and salary['from'] != None:
                salary['message'] = f'{salary["from"]} - {salary["to"]} '
            elif salary['to'] != None:
                salary['message'] = f'до {salary["to"]} '
            else:
                salary['message'] = f'от {salary["from"]} '

            if salary['currency'] != None:
                salary['message'] += salary['currency']

            if salary['gross'] != None:
                salary['message'] += ' (до вычета налогов)' if salary['gross'] else ' (на руки)'
    context = {
        'vacancies': vacancies
    }

    return render(request, 'latest_vacancies/index.html', context)


def get_vacancies():
    url = 'https://api.hh.ru/vacancies'
    profession = 'Тестировщик (QA-инженер)'
    params = {
        "text": profession,
        "search_field": "name",
        "order_by": "publication_time",
        "date_from": (datetime.datetime.now() - datetime.timedelta(1)).isoformat(),
        "page": 0,
        "per_page": 10
    }
    response = requests.get(url, params=params)
    data = response.json()
    vacancies = []
    for vacancy in data.get('items', []):
        id = vacancy['id']
        vacancy_data = requests.get(f"{url}/{id}").json()
        vacancies.append(
            {
                'name': vacancy_data['name'],
                'description': vacancy_data['description'],
                'key_skills': [skill['name'] for skill in vacancy_data.get('key_skills', [])],
                'employer': vacancy_data['employer']['name'],
                'salary': {
                    'currency': vacancy_data['salary']['currency'] if vacancy_data.get('salary') else None,
                    'from': vacancy_data['salary']['from'] if vacancy_data.get('salary') else None,
                    'to': vacancy_data['salary']['to'] if vacancy_data.get('salary') else None,
                    'gross': vacancy_data['salary']['gross'] if vacancy_data.get('salary') else None
                },
                'area': vacancy_data['area']['name'],
                'published_at': vacancy_data['published_at']
            }
        )
    return vacancies
