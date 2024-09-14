# reports/admin.py
from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'generated_by', 'generated_at', 'status')
    list_filter = ('report_type', 'status')


