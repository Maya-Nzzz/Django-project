from django.contrib import admin
from .models import Vacancy

class VacancyAdmin(admin.ModelAdmin):
    list_display = ("name", "salary", "area_name", "date", "short_key_skills")
    search_fields = ("name", "key_skills")
    list_filter = ("area_name", "salary", "date")
    ordering = ("-date",)

    def short_key_skills(self, obj):
        return obj.key_skills[:10] + "..." if (obj.key_skills is not None and len(obj.key_skills) > 50) else obj.key_skills
    short_key_skills.short_description = "Key Skills"

admin.site.register(Vacancy, VacancyAdmin)
