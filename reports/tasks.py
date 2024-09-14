from celery import shared_task
from .models import Report
from borrowing.models import Borrowing
from django.utils.timezone import now
from django.core.files.base import ContentFile
from django.db.models import Count


@shared_task
def generate_most_borrowed_books_report(report_id):
    try:
        report = Report.objects.get(id=report_id)

        most_borrowed_books = (
            Borrowing.objects.values('book__title')
            .annotate(total_borrows=Count('book'))
            .order_by('-total_borrows')[:10]
        )

        file_content = "Book Title,Total Borrows\n"
        for book in most_borrowed_books:
            file_content += f"{book['book__title']},{book['total_borrows']}\n"

        report.file.save(f"most_borrowed_books_{report.generated_at}.csv", ContentFile(file_content))
        report.status = 'success'
        report.save()
    except Exception as e:
        report.status = 'failed'
        report.save()


@shared_task
def generate_late_borrowers_report(report_id):
    try:
        report = Report.objects.get(id=report_id)
        late_borrowings = Borrowing.objects.filter(return_date__lt=now(), actual_return_date__isnull=True)

        file_content = "User,Book Title,Due Date\n"
        for borrowing in late_borrowings:
            file_content += f"{borrowing.user.username},{borrowing.book.title},{borrowing.return_date}\n"

        report.file.save(f"late_borrowers_{report.generated_at}.csv", ContentFile(file_content))
        report.status = 'success'
        report.save()
    except Exception as e:
        report.status = 'failed'
        report.save()


@shared_task
def generate_currently_borrowed_books_report(report_id):
    try:
        report = Report.objects.get(id=report_id)
        currently_borrowed_books = Borrowing.objects.filter(actual_return_date__isnull=True)

        file_content = "User,Book Title,Borrow Date\n"
        for borrowing in currently_borrowed_books:
            file_content += f"{borrowing.user.username},{borrowing.book.title},{borrowing.borrow_date}\n"

        report.file.save(f"currently_borrowed_books_{report.generated_at}.csv", ContentFile(file_content))
        report.status = 'success'
        report.save()
    except Exception as e:
        report.status = 'failed'
        report.save()
