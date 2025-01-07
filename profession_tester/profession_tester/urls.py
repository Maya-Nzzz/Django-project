from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('homepage.urls')),
    path('demand/', include('demand.urls')),
    path('general_statistics/', include('general_statistics.urls')),
    path('geography/', include('geography.urls')),
    path('latest_vacancies/', include('latest_vacancies.urls')),
    path('skills/', include('skills.urls')),
    path('admin/', admin.site.urls),
]
