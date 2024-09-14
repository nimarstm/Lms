from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Report(models.Model):
    REPORT_CHOICES = [
        ('MOST_BORROWED_BOOKS', 'Most Borrowed Books'),
        ('LATE_BORROWERS', 'Late Borrowers'),
        ('CURRENTLY_BORROWED_BOOKS', 'Currently Borrowed Books'),
    ]

    report_type = models.CharField(max_length=50, choices=REPORT_CHOICES)
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='reports/')
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f'{self.get_report_type_display()} by {self.generated_by.username} at {self.generated_at}'
