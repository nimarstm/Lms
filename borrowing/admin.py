from django.contrib import admin
from .models import Borrowing, Reservation
from django import forms
from .models import Borrowing, Book


class BorrowingAdminForm(forms.ModelForm):
    class Meta:
        model = Borrowing
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BorrowingAdminForm, self).__init__(*args, **kwargs)
        self.fields['book'].queryset = Book.objects.filter(is_borrowed=False)


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    form = BorrowingAdminForm
    list_display = ['user', 'book', 'borrow_date', 'due_date', 'return_date', 'status']

    def save_model(self, request, obj, form, change):
        if obj.return_date:
            obj.book.is_borrowed = False
        else:
            obj.book.is_borrowed = True
        obj.book.save()
        super().save_model(request, obj, form, change)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'reserved_at', 'is_active']
    list_filter = ['is_active', 'reserved_at']
    search_fields = ['user__username', 'book__title']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'book')