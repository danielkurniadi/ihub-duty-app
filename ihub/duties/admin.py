from django.contrib import admin
from .models import Duty, DutyManager

class DutyAdmin(admin.ModelAdmin):
    model = Duty

class DutyManagerAdmin(admin.ModelAdmin):
    model = DutyManager

admin.site.register(Duty, DutyAdmin)
admin.site.register(DutyManager, DutyManagerAdmin)
