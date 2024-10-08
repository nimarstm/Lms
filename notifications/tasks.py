from celery import shared_task
from datetime import datetime, timedelta
from django.utils import timezone
from borrowing.models import Borrowing
from notifications.models import Notification


@shared_task
def send_return_reminder():
    now = timezone.now()
    reminder_date = (now + timedelta(days=1))

    borrowings = Borrowing.objects.filter(due_date=reminder_date, status='borrowed')

    for borrowing in borrowings:
        Notification.objects.create(
            user=borrowing.user,
            book=borrowing.book,
            message=f'Reminder: Please return the book "{borrowing.book.title}" by {borrowing.due_date}.'
        )


@shared_task
def send_overdue_alert():
    now = timezone.now()

    borrowings = Borrowing.objects.filter(due_date__lt=now, status='borrowed')

    for borrowing in borrowings:
        Notification.objects.create(
            user=borrowing.user,
            book=borrowing.book,
            message=f'Alert: The book "{borrowing.book.title}" is overdue. Please return it immediately!'
        )
        borrowing.status = 'overdue'
        borrowing.save()
