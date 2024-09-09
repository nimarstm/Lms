from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Book Title"))
    author = models.ForeignKey('Author', on_delete=models.CASCADE, related_name='books', verbose_name=_("Author"))
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name='books',
                                 verbose_name=_("Category"))
    publisher = models.ForeignKey('Publisher', on_delete=models.SET_NULL, null=True, related_name='books',
                                  verbose_name=_("Publisher"))
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    publication_date = models.DateField(verbose_name=_("Publication Date"))
    number_of_pages = models.IntegerField(verbose_name=_("Number of pages"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    available_copies = models.IntegerField(default=0, verbose_name=_("Available Copies"))
    total_copies = models.IntegerField(default=1, verbose_name=_("Total Copies"))
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    is_borrowed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "Books"
        verbose_name = _("Book")
        verbose_name_plural = _("Books")


class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "categories"
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class Author(models.Model):
    first_name = models.CharField(max_length=100, verbose_name=_("Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    biography = models.TextField(null=True, blank=True, verbose_name=_("Biography"))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_("Birth Date"))
    date_of_death = models.DateField(null=True, blank=True, verbose_name=_("Death Date"))

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")


class Publisher(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Address"))
    website = models.URLField(blank=True, null=True, verbose_name=_("Website"))
    contact_email = models.EmailField(blank=True, null=True, verbose_name=_("Email"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Publisher")
        verbose_name_plural = _("Publishers")


class BookCopy(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    copy_number = models.IntegerField()
    is_borrowed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.book.title} - Copy {self.copy_number}"

    class Meta:
        verbose_name = _("BookCopy")
        verbose_name_plural = _("BookCopies")

