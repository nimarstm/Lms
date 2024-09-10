from django.urls import path
from .views import CreateReviewView, BookReviewsListView, UserReviewDetailView

urlpatterns = [

    path('reviews/create/', CreateReviewView.as_view(), name='create-review'),

    path('books/<int:book_id>/reviews/', BookReviewsListView.as_view(), name='book-reviews-list'),
    path('reviews/<int:pk>/', UserReviewDetailView.as_view(), name='user-review-detail'),
]
