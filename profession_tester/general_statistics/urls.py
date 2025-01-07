from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='general_statistics'),
]