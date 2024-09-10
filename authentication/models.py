from django.contrib.auth.models import AbstractUser
from django.db import models


class LibraryUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('librarian', 'Librarian'),
        ('member', 'Member'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    contact_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_librarian(self):
        return self.role == 'librarian'

    @property
    def is_member(self):
        return self.role == 'member'


class MemberProfile(models.Model):
    user = models.OneToOneField(LibraryUser, on_delete=models.CASCADE, related_name='profile')
    membership_date = models.DateField(auto_now_add=True)
    membership_expiry = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
