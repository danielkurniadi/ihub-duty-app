from django.contrib import admin
from .models import Duty, DutyManager

@admin.register(Duty)
class DutyAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('__status__', 'last_active',)
        }),
        ('Duty Timeline', {
            'fields': (('duty_start', 'duty_end'),
            )
        }),
        ('Tasks` Timeline', {
            'fields': (
                ('task1_start', 'task1_end'), ('task2_start', 'task2_end'),
                ('task3_start', 'task3_end')
            )
        }),
        ('Student Assistants', {
            'fields': ('user', 'debtee')
        }),
    )

    list_display = ('__status__', 'duty_start', 'duty_end', 'user', 'last_active')
    list_filter = ('user', 'debtee')

    search_fields = ('duty_start', '__status__', 'user')
    ordering = ('duty_start', 'last_active')
    readonly_fields = [
        '__status__', 'duty_start', 'duty_end',
        'task1_start', 'task1_end', 'task2_start', 'task2_end',
        'task3_start', 'task3_end',
    ]

@admin.register(DutyManager)
class DutyManagerAdmin(admin.ModelAdmin):
    pass
