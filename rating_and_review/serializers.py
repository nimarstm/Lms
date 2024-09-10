from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source='book.title')
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = ['id', 'user', 'book', 'book_title', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']
