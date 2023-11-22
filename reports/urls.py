from django.urls import path
from .views import *

urlpatterns = [
    path('', ReportAPIView.as_view()),
    path('quick/', ReportCacheAPIView.as_view()),
]