from django.contrib import admin
from .models import Borrowing


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'borrow_date', 'due_date', 'return_date', 'status', 'late_fee']
    list_filter = ['status', 'borrow_date']
    search_fields = ['user__username', 'book__title']
