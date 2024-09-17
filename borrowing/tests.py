from datetime import timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from books.models import Author
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from books.models import Book
from borrowing.models import Borrowing, Reservation

User = get_user_model()


class BorrowingModelTest(TestCase):
    def setUp(self):
        author = Author.objects.create(first_name="J.K", last_name="Rowling")
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.book = Book.objects.create(title='Test Book', is_borrowed=False, author=author)
        self.borrowing = Borrowing.objects.create(user=self.user, book=self.book, due_date="2024-09-16")

    def test_borrowing_creation(self):
        self.assertEqual(self.borrowing.user.username, 'testuser')
        self.assertEqual(self.borrowing.book.title, 'Test Book')
        self.assertFalse(self.borrowing.book.is_borrowed)

    def test_is_returned_false_on_creation(self):
        self.assertEqual(self.borrowing.status, "borrowed")


class BorrowingTests(APITestCase):
    due_date = (timezone.now() + timedelta(days=14)).date()

    def setUp(self):
        author = Author.objects.create(first_name="J.K", last_name="Rowling")
        self.admin_user = User.objects.create_user(username='admin', password='adminpass', role='admin')
        self.librarian_user = User.objects.create_user(username='librarian', password='libpass', role='librarian')
        self.member_user = User.objects.create_user(username='member', password='memberpass', role='member')
        self.book1 = Book.objects.create(title="Book 1", is_borrowed=False, author=author, isbn=987654321)
        self.book2 = Book.objects.create(title="Book 2", is_borrowed=True, author=author, isbn=123456789)
        self.borrowing = Borrowing.objects.create(user=self.member_user, book=self.book2, due_date=self.due_date)
        self.client = APIClient()

    def test_list_available_books(self):
        """
    available bok test
        """
        url = reverse('Available-book')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_borrow_book_as_member(self):
        """
member borrow test
        """
        self.client.force_authenticate(user=self.member_user)

        url = reverse('borrowing-list')
        data = {'book': self.book1.id}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_borrow_book_as_librarian(self):
        """
librarian borrow test
        """
        self.client.force_authenticate(user=self.librarian_user)

        url = reverse('borrowing-list')

        data = {
            'book': self.book1.id,
            'due_date': self.due_date,
            'user': self.librarian_user.id
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.get(id=self.book1.id).is_borrowed)

    def test_borrow_book_as_admin(self):
        """
admin borrow test
        """
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('borrowing-list')

        data = {
            'book': self.book1.id,
            'due_date': self.due_date,
            'user': self.librarian_user.id
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.get(id=self.book1.id).is_borrowed)

    def test_borrow_already_borrowed_book(self):
        """
borrow borrowed book test
        """
        self.client.force_authenticate(user=self.librarian_user)
        url = reverse('borrowing-list')

        data = {
            'book': self.book2.id,
            'due_date': self.due_date,
            'user': self.librarian_user.id
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_reservation(self):
        """
reserve borrowed book test
        """
        self.client.force_authenticate(user=self.member_user)
        url = reverse('reserve-book')

        data = {'book': self.book2.id}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Reservation.objects.filter(book=self.book2, user=self.member_user).exists())

    def test_reserve_already_reserved_book(self):
        """
reserve reserved book test
        """
        Reservation.objects.create(user=self.member_user, book=self.book2, is_active=True)
        self.client.force_authenticate(user=self.member_user)
        url = reverse('reserve-book')

        data = {'book': self.book2.id}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_borrowing_history(self):
        """
user borrow history test
        """
        self.client.force_authenticate(user=self.member_user)
        url = reverse('borrow-history')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
