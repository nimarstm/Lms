from django.urls import path
from .views import ReportCreateView, ReportListView

urlpatterns = [
    path('create/', ReportCreateView.as_view(), name='create-report'),
    path('list/', ReportListView.as_view(), name='list-reports'),
]
