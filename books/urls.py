from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BookView, AuthorView, BookCopyView, PublisherView, CategoryView

router = DefaultRouter()
router.register(r'books', BookView, basename='books')
router.register(r'authors', AuthorView, basename='author')
router.register(r'categories', CategoryView)
router.register(r'publishers', PublisherView)
router.register(r'bookcopy', BookCopyView)

urlpatterns = [
    path('', include(router.urls)),



]
