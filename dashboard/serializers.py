"""
Serializers for Dashboard responses (Admin, Student, Instructor).
"""

from rest_framework import serializers


# =========================
# Shared / Common
# =========================

class ActivitySerializer(serializers.Serializer):
    action = serializers.CharField()
    description = serializers.CharField()
    timestamp = serializers.DateTimeField()


class ExamSerializer(serializers.Serializer):
    exam_type = serializers.CharField()
    exam_date = serializers.DateTimeField()
    room = serializers.CharField()


# =========================
# Admin Dashboard
# =========================

class AdminStatisticsSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    active_students = serializers.IntegerField()
    total_courses = serializers.IntegerField()
    active_classes = serializers.IntegerField()
    total_instructors = serializers.IntegerField()
    average_class_size = serializers.FloatField()


class EnrollmentTrendSerializer(serializers.Serializer):
    semester = serializers.CharField()
    academic_year = serializers.IntegerField()
    enrollment_count = serializers.IntegerField()


class AttendanceOverviewSerializer(serializers.Serializer):
    average_attendance_rate = serializers.FloatField()
    classes_below_threshold = serializers.IntegerField()


class AdminDashboardSerializer(serializers.Serializer):
    statistics = AdminStatisticsSerializer()
    enrollment_trends = EnrollmentTrendSerializer(many=True)
    recent_activities = ActivitySerializer(many=True)
    pending_requests = serializers.IntegerField()
    attendance_overview = AttendanceOverviewSerializer()


# =========================
# Student Dashboard
# =========================

class StudentProfileSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    name = serializers.CharField()
    academic_status = serializers.CharField()
    cumulative_gpa = serializers.FloatField()


class StudentSemesterSerializer(serializers.Serializer):
    semester = serializers.CharField()
    academic_year = serializers.IntegerField()
    enrolled_courses = serializers.IntegerField()
    total_credits = serializers.IntegerField()
    semester_gpa = serializers.FloatField()


class EnrolledClassSerializer(serializers.Serializer):
    class_code = serializers.CharField()
    course_name = serializers.CharField()
    instructor_name = serializers.CharField()
    schedule = serializers.CharField()
    current_grade = serializers.CharField(allow_null=True)


class StudentExamSerializer(serializers.Serializer):
    course_name = serializers.CharField()
    exam_type = serializers.CharField()
    exam_date = serializers.DateTimeField()
    room = serializers.CharField()


class RecentGradeSerializer(serializers.Serializer):
    course_name = serializers.CharField()
    assignment_name = serializers.CharField()
    grade = serializers.CharField()
    date = serializers.DateTimeField()


class StudentAttendanceSummarySerializer(serializers.Serializer):
    attendance_rate = serializers.FloatField()
    classes_at_risk = serializers.IntegerField()


class StudentDashboardSerializer(serializers.Serializer):
    student_profile = StudentProfileSerializer()
    current_semester = StudentSemesterSerializer()
    enrolled_classes = EnrolledClassSerializer(many=True)
    upcoming_exams = StudentExamSerializer(many=True)
    recent_grades = RecentGradeSerializer(many=True)
    attendance_summary = StudentAttendanceSummarySerializer()
    unread_notifications = serializers.IntegerField()
    unread_messages = serializers.IntegerField()


# =========================
# Instructor Dashboard
# =========================

class InstructorProfileSerializer(serializers.Serializer):
    name = serializers.CharField()
    department = serializers.CharField()


class InstructorSemesterSerializer(serializers.Serializer):
    semester = serializers.CharField()
    academic_year = serializers.IntegerField()
    total_classes = serializers.IntegerField()
    total_students = serializers.IntegerField()


class InstructorClassSerializer(serializers.Serializer):
    class_code = serializers.CharField()
    course_name = serializers.CharField()
    section = serializers.CharField()
    enrolled_students = serializers.IntegerField()
    schedule = serializers.CharField()
    average_attendance = serializers.FloatField()


class InstructorExamSerializer(serializers.Serializer):
    class_code = serializers.CharField()
    exam_type = serializers.CharField()
    exam_date = serializers.DateTimeField()
    room = serializers.CharField()


class InstructorDashboardSerializer(serializers.Serializer):
    instructor_profile = InstructorProfileSerializer()
    current_semester = InstructorSemesterSerializer()
    my_classes = InstructorClassSerializer(many=True)
    upcoming_exams = InstructorExamSerializer(many=True)
    pending_grading = serializers.IntegerField()
    recent_activities = ActivitySerializer(many=True)
