from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='latest_vacancies'),
]