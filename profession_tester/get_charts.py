import re
import random
from collections import Counter
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from import_csv import get_salary


def get_data_from_csv(vacancies, profession_regex):
    years = range(2007, 2025)
    salary_by_year, count_by_year = calculate_yearly_metrics(vacancies, years)
    professional_vacancies = vacancies[vacancies["name"].str.contains(profession_regex, case=False, na=False)]
    salary_by_year_prof, count_by_year_prof = calculate_yearly_metrics(professional_vacancies, years)
    cities, cities_counts = calculate_city_metrics(vacancies)
    cities_prof, cities_counts_prof = calculate_city_metrics(professional_vacancies)

    return (salary_by_year, count_by_year, salary_by_year_prof, count_by_year_prof, cities, cities_counts, cities_prof,
            cities_counts_prof)


def clean_value(value):
    value = str(value)
    if not value:
        return "Нет данных"
    if '\n' in value:
        return [' '.join(item.strip().split()) for item in value.split('\n')]
    value = re.sub(r'<.*?>', '', value)
    value = ' '.join(value.split())
    return value.strip()


def calculate_yearly_metrics(vacancies, necessary_years):
    filtered_vacancies = vacancies[vacancies["average"] <= 10_000_000]
    salary_by_year = (
        filtered_vacancies.groupby("year")["average"]
        .mean()
        .reindex(necessary_years, fill_value=0).apply(round).to_dict()
    )

    count_by_year = (
        vacancies.groupby("year").size().reindex(necessary_years, fill_value=0).to_dict()
    )

    return salary_by_year, count_by_year


def calculate_city_metrics(vacancies):
    all_vacancies = len(vacancies)
    cities = (
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
    cities_counts = (vacancies.groupby("area_name")
                     .agg(count=("name", "count"))
                     .assign(percent=lambda df: df["count"] / all_vacancies * 100)
                     .sort_values(["percent", "area_name"], ascending=[False, True]).query("percent >= 0.01")
                     .reset_index()
                     .set_index("area_name")["percent"].iloc[:10]
                     .apply(lambda x: f"{x:.2f}".rstrip("0").rstrip("."))
                     .to_dict()
                     )

    return cities, cities_counts


def get_count_year_dynamic(count_by_year, label, file_name):
    years = range(2007, 2025)
    width = 0.4
    x = np.arange(len(years))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width / 2, list(count_by_year.values()), width=width, color=(0 / 255, 100 / 255, 0 / 255, 0.7),
           label=label)
    ax.set_title(label, fontsize=10)
    ax.grid(axis="y")
    ax.legend(fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([str(year) for year in years], rotation=90, fontsize=8)
    ax.tick_params(axis="y", labelsize=8)

    plt.tight_layout()
    plt.savefig(f"static/img/{file_name}.png")
    plt.close(fig)


def get_salary_year_dynamic(salary_by_year, label, file_name):
    years = range(2007, 2025)
    width = 0.4
    x = np.arange(len(years))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width / 2, list(salary_by_year.values()), width=width, color=(0 / 255, 100 / 255, 0 / 255, 0.7),
           label=label)
    ax.set_title(label, fontsize=10)
    ax.grid(axis="y")
    ax.legend(fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([str(year) for year in years], rotation=90, fontsize=8)
    ax.tick_params(axis="y", labelsize=8)

    plt.tight_layout()
    plt.savefig(f"static/img/{file_name}.png")
    plt.close(fig)


def get_top_10_salary_city(cities, label, file_name):
    cities_for_3_graph = [city.replace(" ", "\n").replace("-", "-\n") for city in cities.keys()]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(cities_for_3_graph, list(cities.values()), color=(0 / 255, 100 / 255, 0 / 255, 0.7))
    ax.set_title(label, fontsize=10)
    ax.grid(axis="x")
    yticks_positions = range(len(cities_for_3_graph))
    ax.set_yticks(yticks_positions)
    ax.set_yticklabels(cities_for_3_graph, fontsize=6, ha="right", va="center")
    ax.tick_params(axis="x", labelsize=8)
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(f"static/img/{file_name}.png")
    plt.close(fig)


def get_top_10_vac_city(cities_counts, label, file_name):
    other_cities = 100 - sum(map(float, list(cities_counts.values())))
    pie_data = list(map(float, list(cities_counts.values()))) + [other_cities]
    pie_labels = list(cities_counts.keys()) + ["Другие"]

    green_shades = [mcolors.to_rgba(f"green", alpha=0.7)]
    for _ in range(len(pie_data)):
        green_value = random.uniform(0, 1)
        green_shades.append(mcolors.to_rgba((0, green_value, 0), alpha=0.7))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie(pie_data, labels=pie_labels, colors=green_shades, textprops={"fontsize": 6})
    ax.set_title(label, fontsize=10)

    plt.tight_layout()
    plt.savefig(f"static/img/{file_name}.png")
    plt.close(fig)


def get_top_20_skills():
    filled_skills = vacancies[vacancies['key_skills'].notna()]
    skills = []
    for _, vacancy in filled_skills.iterrows():
        skill = clean_value(vacancy.get("key_skills"))
        if isinstance(skill, list):
            skills.extend(skill)
        else:
            skills.append(skill)
    skill_count = dict(Counter(skills).most_common(20))
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(list(skill_count.keys()), list(skill_count.values()), color=(0 / 255, 100 / 255, 0 / 255, 0.7))
    ax.set_title("ТОП-20 навыков", fontsize=10)
    ax.grid(axis="x")
    yticks_positions = range(20)
    ax.set_yticks(yticks_positions)
    ax.set_yticklabels(skill_count.keys(), fontsize=6, ha="right", va="center")
    ax.tick_params(axis="x", labelsize=8)
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig("static/img/get_top_20_skills.png")
    plt.close(fig)

    return skill_count


if __name__ == '__main__':
    df_currency = pd.read_csv('currency.csv', index_col='date')
    vacancies = pd.read_csv("vacancies_2024.csv", low_memory=False)
    vacancies['date'] = pd.to_datetime(vacancies['published_at'], errors='coerce', utc=True).dt.strftime('%Y-%m')
    vacancies["year"] = pd.to_datetime(vacancies["published_at"], format="%Y-%m-%dT%H:%M:%S%z", utc=True).dt.year
    vacancies["average"] = vacancies.apply(lambda row: get_salary(row, df_currency), axis=1)
    profession = ['Тестировщик (QA-инженер)', 'Тестировщик', 'QA-инженер', 'qa', 'test', 'тест', 'quality assurance']
    profession_regex = '|'.join(map(re.escape, profession))
    salary_by_year, count_by_year, salary_by_year_prof, count_by_year_prof, cities, cities_counts, cities_prof, cities_counts_prof = get_data_from_csv(
        vacancies, profession_regex)
    get_count_year_dynamic(count_by_year, "Динамика количества вакансий по годам", "get_count_year_dynamic")
    get_count_year_dynamic(count_by_year_prof, "Динамика количества вакансий Тестировщик (QA-инженер) по годам",
                           "get_count_year_dynamic_prof")
    get_salary_year_dynamic(salary_by_year, "Динамика уровня зарплат по годам", "get_salary_year_dynamic")
    get_salary_year_dynamic(salary_by_year_prof, "Динамика уровня зарплат вакансии Тестировщик (QA-инженер) по годам",
                            "get_salary_year_dynamic_prof")
    get_top_10_salary_city(cities, "Уровень зарплат по городам", "get_top_10_salary_city")
    get_top_10_salary_city(cities_prof, "Уровень зарплат вакансии Тестировщик (QA-инженер) по городам",
                           "get_top_10_salary_city_prof")
    get_top_10_vac_city(cities_counts, "Доля вакансий по городам", "get_top_10_vac_city")
    get_top_10_vac_city(cities_counts_prof, "Доля вакансий Тестировщик (QA-инженер) по городам",
                        "get_top_10_vac_city_prof")
    get_top_20_skills()
