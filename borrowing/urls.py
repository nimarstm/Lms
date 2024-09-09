from django.urls import path
from .views import BorrowingListCreateView, BorrowingDetailView,AvailableBooksListView

urlpatterns = [
    path('borrowings/', BorrowingListCreateView.as_view(), name='borrowing-list'),
    path('borrowings/<int:pk>/', BorrowingDetailView.as_view(), name='borrowing-detail'),
    path('borrowings/available/', AvailableBooksListView.as_view(), name='Available-book'),

]
