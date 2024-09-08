from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Borrowing
from .serializers import BorrowingSerializer
from django.utils import timezone
from utils.permissions import IsAdminOrLibrarianOrReadOnly, IsAdminOrLibrarianOrOwner


class BorrowingListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrLibrarianOrReadOnly]
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BorrowingDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrLibrarianOrOwner]
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def perform_update(self, serializer):
        instance = self.get_object()
        if not instance.return_date:
            instance.return_date = timezone.now()
            instance.save()
        serializer.save()
