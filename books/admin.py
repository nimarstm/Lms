from django.contrib import admin
from .models import Book, Category, BookCopy, Author, Publisher


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'date_of_birth', 'date_of_death')
    search_fields = ('first_name', 'last_name')
    list_filter = ('date_of_birth', 'date_of_death')
    ordering = ['last_name', 'first_name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'contact_email')
    search_fields = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'publisher', 'isbn', 'publication_date', 'total_copies', 'available_copies')
    list_filter = ('author', 'category', 'publisher', 'publication_date')
    search_fields = ('title', 'isbn', 'author__first_name', 'author__last_name')
    ordering = ['title']
    fields = ('title', 'author', 'category', 'publisher', 'publication_date', 'isbn', 'description', 'total_copies', 'available_copies', 'cover_image')


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('book', 'copy_number', 'is_borrowed')
    list_filter = ('is_borrowed', 'book')
    search_fields = ('book__title', 'copy_number')
    ordering = ['book', 'copy_number']
