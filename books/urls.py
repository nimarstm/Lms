from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BookView, AuthorView, BookCopyView, PublisherView, CategoryView

router = DefaultRouter()
router.register(r'books', BookView, basename='books')
router.register(r'authors', AuthorView, basename='author')
router.register(r'categories', CategoryView,basename='category')
router.register(r'publishers', PublisherView,basename='publisher')
router.register(r'bookcopy', BookCopyView,basename='bookcopy')

urlpatterns = [
    path('', include(router.urls)),



]
