"""
URL configuration for notifications app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from notifications.views import (
    NotificationViewSet, MessageViewSet,
    StudentRequestViewSet, ReportViewSet
)

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'messages', MessageViewSet, basename='messages')
router.register(r'student-requests', StudentRequestViewSet, basename='student-requests')
router.register(r'reports', ReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]