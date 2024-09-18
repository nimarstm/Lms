from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from books.models import Book, Author
from .models import Review
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Review

User = get_user_model()


class ReviewModelTest(TestCase):

    def setUp(self):
        self.author = Author.objects.create(first_name="John", last_name="Doe", biography="Author biography")
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book = Book.objects.create(
            title='Test Book',
            author=self.author,
            isbn='1234567890123',
            publication_date='2024-01-01',
            number_of_pages=100,
            total_copies=5,
            available_copies=5
        )
        self.review = Review.objects.create(
            user=self.user,
            book=self.book,
            rating=5,
            comment='Excellent book!'
        )

    def test_review_creation(self):
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.book, self.book)
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, 'Excellent book!')
        self.assertTrue(self.review.created_at)

    def test_unique_review_constraint(self):
        with self.assertRaises(Exception):
            Review.objects.create(
                user=self.user,
                book=self.book,
                rating=4,
                comment='Another comment'
            )

    def test_review_str(self):
        self.assertEqual(str(self.review), f'Review for {self.book.title} by {self.user.username}')


class ReviewAPITest(APITestCase):

    def setUp(self):
        self.author = Author.objects.create(first_name="John", last_name="Doe", biography="Author biography")
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book = Book.objects.create(
            title='Test Book',
            author=self.author,
            isbn='1234567890123',
            publication_date='2024-01-01',
            number_of_pages=100,
            total_copies=5,
            available_copies=5
        )
        self.book2 = Book.objects.create(
            title='Test Book2',
            author=self.author,
            isbn='1234567890132',
            publication_date='2024-01-02',
            number_of_pages=120,
            total_copies=6,
            available_copies=5
        )
        self.client.login(username='testuser', password='testpassword')

        self.review = Review.objects.create(
            user=self.user,
            book=self.book,
            rating=5,
            comment='Excellent book!'
        )
        self.book_reviews_url = f'books/{self.book.id}/reviews/'
        self.user_review_detail_url = f'reviews/{self.review.id}/'

    def test_create_review(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'book': self.book2.id,
            'rating': 4,
            'comment': 'Good book!'

        }
        url = reverse('create-review')
        response = self.client.post(url, data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)

    def test_create_review_duplicate(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'book': self.book.id,
            'rating': 4,
            'comment': 'Another comment'
        }
        url = reverse('create-review')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_reviews_for_book(self):
        url = reverse('book-reviews-list', kwargs={'book_id': self.book.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_review(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-review-detail', kwargs={'pk': self.review.id})
        data = {
            'book': self.book.id,
            'rating': 3,
            'comment': 'Updated comment!'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 3)
        self.assertEqual(self.review.comment, 'Updated comment!')
