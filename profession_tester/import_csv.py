import pandas as pd
import sqlite3


def currency_coefficient(row, currency):
    if currency == "RUR":
        return 1
    coefficients = df_currency[df_currency.index == row["date"]]
    if coefficients.empty or pd.isna(coefficients[currency]).all():
        return None
    return coefficients[currency].values[0]


def get_salary(row):
    salary_to = row['salary_to']
    salary_from = row['salary_from']
    if pd.isna(row['salary_currency']):
        return None
    coefficient = currency_coefficient(row, row["salary_currency"])
    if coefficient is None:
        return None
    if pd.notna(salary_from) and pd.notna(salary_to):
        return (salary_to + salary_from) / 2 * coefficient
    if pd.notna(salary_to):
        return salary_to * coefficient
    if pd.notna(salary_from):
        return salary_from * coefficient
    return None



if __name__ == "__main__":
    df_currency = pd.read_csv('currency.csv', index_col='date')
    csv_merged = pd.read_csv('vacancies_2024.csv', low_memory=False)
    csv_merged['date'] = pd.to_datetime(csv_merged['published_at'], errors='coerce', utc=True).dt.strftime('%Y-%m')
    csv_merged['salary'] = csv_merged.apply(lambda row: get_salary(row), axis=1)
    data = csv_merged[['name', 'key_skills', 'salary', 'area_name', 'date']].copy()
    data.reset_index(drop=True, inplace=True)
    data['id'] = data.index + 1
    data = data[['id'] + ['name', 'key_skills', 'salary', 'area_name', 'date']]
    conn = sqlite3.connect("db.sqlite3")
    data.to_sql("vacancies", conn, if_exists='replace', index=False)
    conn.close()
