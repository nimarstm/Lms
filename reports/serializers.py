from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'report_type', 'generated_at', 'generated_by', 'file', 'status']
        read_only_fields = ['generated_at', 'generated_by', 'file', 'status']
