from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Book, Author, Category, BookCopy, Publisher
from .serializers import BookSerializer, AuthorSerializer, CategorySerializer, PublisherSerializer, BookCopySerializer
from rest_framework import viewsets
from rest_framework import permissions


# Create your views here.
class BookView(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author__first_name', 'author__last_name', 'category__title', 'publisher__name']


class AuthorView(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['first_name', 'last_name', 'date_of_birth']


class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PublisherView(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class BookCopyView(viewsets.ModelViewSet):
    queryset = BookCopy.objects.all()
    serializer_class = BookCopySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_borrowed', 'book']


