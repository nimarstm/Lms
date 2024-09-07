from rest_framework import serializers
from .models import Author, Category, Publisher, BookCopy, Book


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'biography', 'date_of_birth', 'date_of_death']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'description']


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'address', 'website', 'contact_email']


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'category', 'publisher', 'publication_date', 'isbn', 'description',
                  'total_copies', 'available_copies', 'cover_image', 'number_of_pages']


class BookCopySerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = BookCopy
        fields = ['id', 'book', 'copy_number', 'is_borrowed']