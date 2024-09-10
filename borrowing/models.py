from django.db import models
from django.conf import settings
from books.models import Book
from django.contrib.auth.models import User

from datetime import timedelta


class Borrowing(models.Model):
    STATUS_CHOICES = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrowings')
    book = models.ForeignKey(Book(is_borrowed=False), on_delete=models.CASCADE, related_name='borrowings')
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='borrowed')
    late_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)

    def calculate_late_fee(self):

        if self.return_date and self.return_date > self.due_date:
            delay_days = (self.return_date - self.due_date).days
            self.late_fee = delay_days * 1.0
        return self.late_fee

    def save(self, *args, **kwargs):
        if self.return_date and self.return_date > self.due_date:
            self.status = 'overdue'
            self.calculate_late_fee()
        elif self.return_date:
            self.status = 'returned'
        super(Borrowing, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title} on {self.borrow_date}"


class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reservations', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='reservations', on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Reservation: {self.book.title} by {self.user.username}'
