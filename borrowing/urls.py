from django.urls import path
from .views import BorrowingListCreateView, BorrowingDetailView, AvailableBooksListView, ReserveBookView, \
    UserReservationsListView, UserBorrowingHistoryView

urlpatterns = [
    path('borrowings/', BorrowingListCreateView.as_view(), name='borrowing-list'),
    path('borrowings/<int:pk>/', BorrowingDetailView.as_view(), name='borrowing-detail'),
    path('borrowings/available/', AvailableBooksListView.as_view(), name='Available-book'),
    path('reserve/', ReserveBookView.as_view(), name='reserve-book'),
    path('reservations/', UserReservationsListView.as_view(), name='user-reservations'),
    path('borrow-history/', UserBorrowingHistoryView.as_view(), name='borrow-history'),

]
