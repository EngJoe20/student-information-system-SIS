"""
URL configuration for grades app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from grades.views import GradeViewSet

router = DefaultRouter()
router.register(r'grades', GradeViewSet, basename='grades')

urlpatterns = [
    path('', include(router.urls)),
]