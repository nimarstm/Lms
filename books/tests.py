from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from books.models import Book, Author, Category, Publisher, BookCopy
from django.utils import timezone

User = get_user_model()


class BookModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Fiction", description="Fictional books")
        self.author = Author.objects.create(first_name="John", last_name="Doe", biography="Author biography")
        self.publisher = Publisher.objects.create(name="Best Publisher", address="123 Main St")

        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            category=self.category,
            publisher=self.publisher,
            isbn="1234567890123",
            publication_date=timezone.now().date(),
            number_of_pages=300,
            description="A test book",
            available_copies=5,
            total_copies=5
        )

    def test_book_creation(self):
        """ book creation test """
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.author, self.author)
        self.assertEqual(self.book.category, self.category)
        self.assertEqual(self.book.publisher, self.publisher)
        self.assertEqual(self.book.isbn, "1234567890123")

    def test_average_rating_no_reviews(self):
        """ avrage rating of no reviewed book test """
        self.assertEqual(self.book.average_rating(), "-")

    def test_book_string_representation(self):
        """ book representation test"""
        self.assertEqual(str(self.book), "Test Book")


class AuthorModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            first_name="jk",
            last_name="rowling",
            biography="Author biography",
            date_of_birth=timezone.now().date()
        )

    def test_author_creation(self):
        """ author model creation test"""
        self.assertEqual(self.author.first_name, "jk")
        self.assertEqual(self.author.last_name, "rowling")
        self.assertEqual(str(self.author), "jk rowling")


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Science", description="Science related books")

    def test_category_creation(self):
        """ category  model creation test """
        self.assertEqual(self.category.title, "Science")
        self.assertEqual(str(self.category), "Science")


class PublisherModelTest(TestCase):
    def setUp(self):
        self.publisher = Publisher.objects.create(
            name="Best Publisher",
            address="address",
            website="https://bestpublisher.com",
            contact_email="info@bestpublisher.com"
        )

    def test_publisher_creation(self):
        """publisher model creation test """
        self.assertEqual(self.publisher.name, "Best Publisher")
        self.assertEqual(self.publisher.address, "address")
        self.assertEqual(str(self.publisher), "Best Publisher")


class BookCopyModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name="jk", last_name="rowling")
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            isbn="1234567890123",
            available_copies=1,
            total_copies=1
        )
        self.book_copy = BookCopy.objects.create(book=self.book, copy_number=1, is_borrowed=False)

    def test_book_copy_creation(self):
        """ book copy model creation test """
        self.assertEqual(self.book_copy.book, self.book)
        self.assertEqual(self.book_copy.copy_number, 1)
        self.assertEqual(str(self.book_copy), f"{self.book.title} - Copy 1")


################################################

class BookViewTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Fiction", description="Fictional books")
        self.author = Author.objects.create(first_name="John", last_name="Doe", biography="Author biography")
        self.publisher = Publisher.objects.create(name="Best Publisher", address="123 Main St")
        self.librarian_user = User.objects.create_user(username='member', password='memberpass', role='librarian')

        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            category=self.category,
            publisher=self.publisher,
            isbn="1234567890123",
            publication_date=timezone.now().date(),
            available_copies=5,
            total_copies=5
        )

    def test_list_books(self):
        """ book list show test """
        url = reverse('books-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Book')

    def test_create_book(self):
        """ book creation test """
        self.client.force_authenticate(user=self.librarian_user)
        url = reverse('books-list')
        data = {
            "title": "New Test Book",
            "author": self.author.id,
            "category": self.category.id,
            "publisher": self.publisher.id,
            "isbn": "567894321588",
            "publication_date": timezone.now().date(),
            "available_copies": 4,
            "total_copies": 5
        }
        response = self.client.post(url, data)
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_update_book(self):
        """ book update test """
        self.client.force_authenticate(user=self.librarian_user)
        url = reverse('books-detail', args=[self.book.id])
        data = {
            "title": "Updated Test Book",
            "author": self.author.id,
            "category": self.category.id,
            "publisher": self.publisher.id,
            "isbn": "1234567890123",
            "publication_date": timezone.now().date(),
            "available_copies": 4,
            "total_copies": 5
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated Test Book")

    def test_filter_books_by_author(self):
        """ filter book by author test"""
        url = reverse('books-list') + f'?author__first_name=John&author__last_name=Doe'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['author']['first_name'], 'John')


class AuthorViewTests(APITestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name="John", last_name="Doe", biography="Author biography")
        self.librarian_user = User.objects.create_user(username='librarian', password='librarianpass', role='librarian')

    def test_list_authors(self):
        """ author list show test """
        url = reverse('author-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_author(self):
        """ author creation test """
        self.client.force_authenticate(user=self.librarian_user)
        url = reverse('author-list')
        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "biography": "Biography of Jane Smith"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), 2)

    def test_filter_author_by_name(self):
        """filter author by name test """
        url = reverse('author-list') + '?first_name=John&last_name=Doe'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], 'John')


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Fiction", description="Fictional books")
        self.librarian_user = User.objects.create_user(username='librarian', password='librarianpass', role='librarian')

    def test_list_categories(self):
        """ category show test """
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_category(self):
        """ category creation test """
        self.client.force_authenticate(user=self.librarian_user)
        url = reverse('category-list')
        data = {
            "title": "Science",
            "description": "Science related books"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)


class PublisherViewTests(APITestCase):
    def setUp(self):
        self.publisher = Publisher.objects.create(name="Best Publisher", address="123 Main St")
        self.librarian_user = User.objects.create_user(username='librarian', password='librarianpass', role='librarian')

    def test_list_publishers(self):
        """publisher list show test"""
        url = reverse('publisher-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_publisher(self):
        """ publisher creation test """
        self.client.force_authenticate(user=self.librarian_user)
        url = reverse('publisher-list')
        data = {
            "name": "New Publisher",
            "address": "456 New St",
            "website": "https://newpublisher.com",
            "contact_email": "pub@newpublisher.com"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Publisher.objects.count(), 2)

    class BookCopyViewTests(APITestCase):
        def setUp(self):
            self.author = Author.objects.create(first_name="John", last_name="Doe")
            self.librarian_user = User.objects.create_user(username='librarian', password='librarianpass',
                                                           role='librarian')
            self.book = Book.objects.create(
                title="Test Book",
                author=self.author,
                isbn="1234567890123",
                available_copies=1,
                total_copies=1
            )
            self.book_copy = BookCopy.objects.create(book=self.book, copy_number=1, is_borrowed=False)

        def test_list_book_copies(self):
            """ book copy list show test """
            url = reverse('bookcopy-list')
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)

        def test_create_book_copy(self):
            """ book copy creation test """
            self.client.force_authenticate(user=self.librarian_user)
            url = reverse('bookcopy-list')
            data = {
                "book": self.book.id,
                "copy_number": 2,
                "is_borrowed": False
            }
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(BookCopy.objects.count(), 2)
