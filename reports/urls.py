from django.urls import path
from .views import *

urlpatterns = [
    path('', ReportAPIView.as_view()),
]