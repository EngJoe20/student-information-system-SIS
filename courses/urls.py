"""
URL configuration for courses app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from courses.views import CourseViewSet, ClassViewSet, RoomViewSet, ExamViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'classes', ClassViewSet, basename='classes')
router.register(r'rooms', RoomViewSet, basename='rooms')
router.register(r'exams', ExamViewSet, basename='exams')

urlpatterns = [
    path('', include(router.urls)),
]