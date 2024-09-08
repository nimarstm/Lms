from rest_framework import serializers
from .models import Borrowing
from django.utils import timezone
from datetime import timedelta


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ['id', 'user', 'book', 'borrow_date', 'due_date', 'return_date', 'status', 'late_fee']
        read_only_fields = ['borrow_date', 'late_fee', 'status']

    def validate(self, data):
        if data['due_date'] <= timezone.now():
            raise serializers.ValidationError("Due date must be in the future.")
        return data
