from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from reports.models import Report
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from unittest.mock import patch, MagicMock
from .tasks import generate_most_borrowed_books_report

User = get_user_model()


class ReportModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    @patch('django.db.models.fields.files.FieldFile.save', MagicMock(name="save"))
    def test_create_report(self):
        test_file = SimpleUploadedFile("report.pdf", b"file_content", content_type="application/pdf")
        report = Report.objects.create(
            report_type='MOST_BORROWED_BOOKS',
            generated_by=self.user,
            file=test_file,
            status='completed'
        )

        self.assertEqual(report.report_type, 'MOST_BORROWED_BOOKS')
        self.assertEqual(report.generated_by, self.user)
        self.assertEqual(report.status, 'completed')
        self.assertTrue(report.file.name.startswith('report'))
        self.assertIsNotNone(report.generated_at)

    @patch('django.db.models.fields.files.FieldFile.save', MagicMock(name="save"))
    def test_str_method(self):
        test_file = SimpleUploadedFile("report.pdf", b"file_content", content_type="application/pdf")
        report = Report.objects.create(
            report_type='LATE_BORROWERS',
            generated_by=self.user,
            file=test_file,
            status='pending'
        )

        expected_str = f'Late Borrowers by {self.user.username} at {report.generated_at}'
        self.assertEqual(str(report), expected_str)

    @patch('django.db.models.fields.files.FieldFile.save', MagicMock(name="save"))
    def test_report_status_default(self):
        test_file = SimpleUploadedFile("report.pdf", b"file_content", content_type="application/pdf")
        report = Report.objects.create(
            report_type='CURRENTLY_BORROWED_BOOKS',
            generated_by=self.user,
            file=test_file
        )

        self.assertEqual(report.status, 'pending')


class ReportAPITest(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin', password='password', role='admin')
        self.librarian_user = User.objects.create_user(username='librarian', password='password', role='librarian')
        self.client = APIClient()

        self.report_create_url = reverse('create-report')
        self.report_list_url = reverse('list-reports')

    @patch('reports.tasks.generate_late_borrowers_report.delay')
    def test_create_report_as_librarian(self, mock_task):
        self.client.force_authenticate(user=self.librarian_user)
        data = {
            'report_type': 'LATE_BORROWERS'
        }
        response = self.client.post(self.report_create_url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Report.objects.count(), 1)
        mock_task.assert_called_once()

    @patch('reports.tasks.generate_late_borrowers_report.delay')
    def test_create_report_as_admin(self, mock_task):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'report_type': 'LATE_BORROWERS'
        }
        response = self.client.post(self.report_create_url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Report.objects.count(), 1)
        mock_task.assert_called_once()

    def test_create_report_without_permission(self):
        regular_user = User.objects.create_user(username='regular', password='password', role='member')

        self.client.force_authenticate(user=regular_user)

        data = {
            'report_type': 'MOST_BORROWED_BOOKS'
        }

        response = self.client.post(self.report_create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_reports_as_admin(self):
        Report.objects.create(report_type='MOST_BORROWED_BOOKS', generated_by=self.admin_user)
        Report.objects.create(report_type='LATE_BORROWERS', generated_by=self.admin_user)

        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.report_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_reports_as_librarian(self):
        Report.objects.create(report_type='MOST_BORROWED_BOOKS', generated_by=self.librarian_user)
        Report.objects.create(report_type='LATE_BORROWERS', generated_by=self.admin_user)

        self.client.force_authenticate(user=self.librarian_user)

        response = self.client.get(self.report_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_reports_without_permission(self):
        regular_user = User.objects.create_user(username='regular', password='password', role='member')

        self.client.force_authenticate(user=regular_user)

        response = self.client.get(self.report_list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ReportTasksTest(TestCase):
    def setUp(self):
        self.report = Report.objects.create(
            report_type='MOST_BORROWED_BOOKS',
            generated_by=self._create_user(),
            status='pending',
        )

    def _create_user(self):
        return User.objects.create(username='testuser', password='password')

    @patch('django.db.models.fields.files.FieldFile.save', MagicMock(name="save"))
    @patch('reports.tasks.Borrowing.objects')
    def test_generate_most_borrowed_books_report_success(self, mock_borrowing_objects):
        mock_borrowing = MagicMock()
        mock_borrowing.values.return_value.annotate.return_value.order_by.return_value = [
            {'book__title': 'Book 1', 'total_borrows': 5},
            {'book__title': 'Book 2', 'total_borrows': 3},
        ]
        mock_borrowing_objects.values.return_value = mock_borrowing

        generate_most_borrowed_books_report(self.report.id)

        self.report.refresh_from_db()
        self.assertEqual(self.report.status, 'success')

    @patch('django.db.models.fields.files.FieldFile.save', MagicMock(name="save"))
    @patch('reports.tasks.Borrowing.objects')
    def test_generate_most_borrowed_books_report_failure(self, mock_borrowing_objects):
        mock_borrowing_objects.values.side_effect = Exception('Database error')

        generate_most_borrowed_books_report(self.report.id)

        self.report.refresh_from_db()
        self.assertEqual(self.report.status, 'failed')
