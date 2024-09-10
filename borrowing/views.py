from rest_framework import generics, permissions, status,serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from books.models import Book
from books.serializers import BookSerializer
from .models import Borrowing, Reservation
from .serializers import BorrowingSerializer, ReservationSerializer
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


class ReserveBookView(generics.CreateAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        book_id = self.request.data.get('book')
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise serializers.ValidationError('Book does not exist.')

        if not book.is_borrowed:
            raise serializers.ValidationError('This book has not been borrowed and cannot be reserved.')

        if Reservation.objects.filter(book=book, is_active=True).exists():
            raise serializers.ValidationError('This book has already been reserved.')

        serializer.save(user=self.request.user, book=book)


class UserReservationsListView(generics.ListAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user, is_active=True)


class UserBorrowingHistoryView(generics.ListAPIView):
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Borrowing.objects.filter(user=self.request.user).order_by('borrow_date')
