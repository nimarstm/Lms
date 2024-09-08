from django_filters.rest_framework import DjangoFilterBackend

from .models import Book, Author, Category, BookCopy, Publisher
from .serializers import BookSerializer, AuthorSerializer, CategorySerializer, PublisherSerializer, BookCopySerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from utils.permissions import IsAdminOrLibrarianOrReadOnly


# Create your views here.
class BookView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrLibrarianOrReadOnly]
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author__first_name', 'author__last_name', 'category__title', 'publisher__name']


class AuthorView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrLibrarianOrReadOnly]
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['first_name', 'last_name', 'date_of_birth']


class CategoryView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrLibrarianOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PublisherView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrLibrarianOrReadOnly]
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class BookCopyView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrLibrarianOrReadOnly]
    queryset = BookCopy.objects.all()
    serializer_class = BookCopySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_borrowed', 'book']
