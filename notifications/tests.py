from django.test import TestCase
from django.contrib.auth import get_user_model
from books.models import Book, Author
from .models import Notification
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta
from borrowing.models import Borrowing
from .tasks import send_return_reminder, send_overdue_alert

User = get_user_model()


class NotificationModelTest(TestCase):
    def setUp(self):
        author = Author.objects.create(first_name="J.K", last_name="Rowling")
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.book = Book.objects.create(title="Test Book", isbn="1234567890123", author=author, available_copies=5,
                                        total_copies=5)

    def test_create_notification(self):
        notification = Notification.objects.create(
            user=self.user,
            book=self.book,
            message="Your reserved book is available now."
        )
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.book, self.book)
        self.assertEqual(notification.message, "Your reserved book is available now.")

    def test_unread_notifications(self):
        notification1 = Notification.objects.create(
            user=self.user,
            book=self.book,
            message="Your reserved book is available now."
        )
        notification2 = Notification.objects.create(
            user=self.user,
            book=self.book,
            message="A new book has been added to your category.",
            is_read=True
        )

        unread_notifications = Notification.objects.filter(user=self.user, is_read=False)
        self.assertEqual(unread_notifications.count(), 1)
        self.assertEqual(unread_notifications.first(), notification1)

    def test_mark_notification_as_read(self):
        notification = Notification.objects.create(
            user=self.user,
            book=self.book,
            message="Your reserved book is available now."
        )
        notification.is_read = True
        notification.save()

        updated_notification = Notification.objects.get(id=notification.id)
        self.assertTrue(updated_notification.is_read)

    def test_delete_notification(self):
        notification = Notification.objects.create(
            user=self.user,
            book=self.book,
            message="Your reserved book is available now."
        )
        notification.delete()

        self.assertEqual(Notification.objects.count(), 0)


class NotificationListViewTest(APITestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name="J.K", last_name="Rowling")
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.book = Book.objects.create(title="Test Book", isbn="1234567890123", author=self.author, available_copies=5,
                                        total_copies=5)
        self.notification = Notification.objects.create(
            user=self.user,
            book=self.book,
            message="Your reserved book is available now."
        )
        self.url = reverse('notifications-list')

    def test_retrieve_notifications_for_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message'], "Your reserved book is available now.")

    def test_notifications_marked_as_read_after_retrieval(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification.objects.get(id=self.notification.id)
        self.assertFalse(notification.is_read)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.seen_at)




class SendReturnReminderTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name="J.K", last_name="Rowling")
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.book = Book.objects.create(title="Test Book", isbn="1234567890123", author=self.author, available_copies=5,
                                        total_copies=5)
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            due_date=(timezone.now() + timedelta(days=1)),
            status='borrowed'
        )

    @patch('notifications.tasks.Notification.objects.create')
    def test_send_return_reminder_creates_notification(self, mock_create):
        send_return_reminder()

        mock_create.assert_called_once_with(
            user=self.borrowing.user,
            book=self.book,
            message=f'Reminder: Please return the book "{self.borrowing.book.title}" by {self.borrowing.due_date}.'
        )


class SendOverdueAlertTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.author = Author.objects.create(first_name="J.K", last_name="Rowling")
        self.book = Book.objects.create(title="Test Book", author=self.author, isbn="1234567890123")

        self.borrowing1 = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            due_date=timezone.now() - timedelta(days=5),
            status='borrowed'
        )
        self.borrowing2 = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            due_date=timezone.now() - timedelta(days=3),
            status='borrowed'
        )

    def test_send_overdue_alert_creates_notifications_and_updates_status(self):
        send_overdue_alert()

        notifications = Notification.objects.filter(user=self.user)
        self.assertEqual(notifications.count(), 2)

        self.borrowing1.refresh_from_db()
        self.borrowing2.refresh_from_db()

        self.assertEqual(self.borrowing1.status, 'overdue')
        self.assertEqual(self.borrowing2.status, 'overdue')
