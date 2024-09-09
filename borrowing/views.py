from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from books.models import Book
from books.serializers import BookSerializer
from .models import Borrowing
from .serializers import BorrowingSerializer
from django.utils import timezone
from utils.permissions import IsAdminOrLibrarianOrReadOnly, IsAdminOrLibrarianOrOwner


class BorrowingListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrLibrarianOrReadOnly]
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def perform_create(self, serializer):
        borrowing = serializer.save(user=self.request.user)

        borrowing.book.is_borrowed = True
        borrowing.book.save()

    def perform_update(self, serializer):
        borrowing = self.get_object()
        if not borrowing.return_date:
            borrowing.return_date = timezone.now()
            borrowing.book.is_borrowed = False
            borrowing.book.save()
        serializer.save()


class BorrowingDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrLibrarianOrReadOnly]
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def perform_update(self, serializer):
        instance = self.get_object()
        if not instance.return_date:
            instance.return_date = timezone.now()
            instance.save()
        serializer.save()


class AvailableBooksListView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrLibrarianOrReadOnly]
    queryset = Book.objects.filter(is_borrowed=False)
    serializer_class = BookSerializer
