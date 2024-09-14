from rest_framework import generics
from .models import Report
from .serializers import ReportSerializer
from .tasks import generate_most_borrowed_books_report, generate_late_borrowers_report, generate_currently_borrowed_books_report
from utils.permissions import IsAdminOrLibrarian


class ReportCreateView(generics.CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAdminOrLibrarian]

    def perform_create(self, serializer):
        report = serializer.save(generated_by=self.request.user)
        if report.report_type == 'MOST_BORROWED_BOOKS':
            generate_most_borrowed_books_report.delay(report.id)
        elif report.report_type == 'LATE_BORROWERS':
            generate_late_borrowers_report.delay(report.id)
        elif report.report_type == 'CURRENTLY_BORROWED_BOOKS':
            generate_currently_borrowed_books_report.delay(report.id)


class ReportListView(generics.ListAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAdminOrLibrarian]
