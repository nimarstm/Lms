from rest_framework import serializers
from .models import Borrowing, Reservation
from django.utils import timezone
from datetime import timedelta


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ['id', 'user', 'book', 'borrow_date', 'due_date', 'return_date', 'status', 'late_fee']
        read_only_fields = ['borrow_date', 'late_fee', 'status']

    def validate(self, data):
        book = data.get('book')
        if book.is_borrowed:
            raise serializers.ValidationError("This book is already borrowed and cannot be borrowed again.")

        if data['due_date'] <= timezone.now():
            raise serializers.ValidationError("Due date must be in the future.")

        return data


class ReservationSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source='book.title')
    book = serializers.HiddenField(default=None)

    class Meta:
        model = Reservation
        fields = ['id', 'book_title', 'reserved_at', 'is_active','book']