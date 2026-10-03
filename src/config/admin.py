from django.contrib import admin, messages
from django_celery_beat.models import PeriodicTask
from django_celery_beat.admin import PeriodicTaskAdmin


def run_selected_tasks(modeladmin, request, queryset):
    from config.celery import app

    for periodic_task in queryset:
        app.send_task(periodic_task.task)

    messages.success(
        request,
        "Selected tasks have been queued."
    )


run_selected_tasks.short_description = "Run selected tasks now"


admin.site.unregister(PeriodicTask)


@admin.register(PeriodicTask)
class CustomPeriodicTaskAdmin(PeriodicTaskAdmin):
    actions = [run_selected_tasks]
