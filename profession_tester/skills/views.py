import re
from collections import Counter
from django.shortcuts import render
from demand.models import Vacancy
from general_statistics.views import declension
from get_charts import clean_value


def index(request):
    profession = ['Тестировщик (QA-инженер)', 'Тестировщик', 'QA-инженер', 'qa', 'test', 'тест', 'quality assurance']
    profession_regex = '|'.join(map(re.escape, profession))
    data_get_top_20_skills = (Vacancy
                              .objects
                              .filter(name__regex=profession_regex)
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

    context = {
        'title': f"Из {declension(len(set(skills)), ['скилла', 'скиллов', 'скиллов'])}, самыми популярными в профессии Тестировщика являются:",
        'result_data_get_top_20_skills': [
            {
                'first': f"{declension(row[1], ['раз', 'раза', 'раз'])}",
                'second': str(row[0])
            }
            for row in dict(Counter(skills).most_common(20)).items()
        ],
    }

    return render(request, 'skills/index.html', context)
