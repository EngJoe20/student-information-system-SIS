"""
URL configuration for students app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from students.views import StudentViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='students')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollments')

urlpatterns = [
    path('', include(router.urls)),
]