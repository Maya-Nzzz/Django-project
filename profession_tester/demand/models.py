from django.db import models


class SiteUser(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def get_name(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        db_table = 'site_users'


class Vacancy(models.Model):
    name = models.CharField(max_length=256)
    salary = models.FloatField(null=True, blank=True)
    area_name = models.CharField(max_length=256)
    date = models.CharField(max_length=32)
    key_skills = models.TextField()

    class Meta:
        db_table = 'vacancies'
# python manage.py migrate
