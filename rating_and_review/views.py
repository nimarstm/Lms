from rest_framework import generics, serializers, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Review
from books.models import Book
from .serializers import ReviewSerializer


class CreateReviewView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        book_id = self.request.data.get('book')
        book = Book.objects.get(id=book_id)

        if Review.objects.filter(user=self.request.user, book=book).exists():
            raise serializers.ValidationError('You have already reviewed this book.')

        serializer.save(user=self.request.user, book=book)


class BookReviewsListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        book_id = self.kwargs['book_id']
        return Review.objects.filter(book_id=book_id)


class UserReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()
