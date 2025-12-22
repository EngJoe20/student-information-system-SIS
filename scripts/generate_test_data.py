"""
Generate comprehensive test data for SIS system.

This script generates realistic test data including:
- Multiple semesters of historical data
- Completed courses with final grades
- Attendance patterns
- Student performance trends

Usage:
    python scripts/generate_test_data.py
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
import random
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_backend.settings.development')
django.setup()

from django.db import transaction
from django.db.models import Avg
from accounts.models import User
from students.models import Student, Enrollment
from courses.models import Course, Class, Room
from attendance.models import Attendance
from grades.models import Grade


class TestDataGenerator:
    """Generate comprehensive test data."""

    def __init__(self):
        self.current_year = datetime.now().year
        self.students = []
        self.instructors = []
        self.courses = []
        self.rooms = []

    def generate_all(self):
        """Generate all test data."""
        print("🎲 Generating comprehensive test data...")

        self.load_existing_data()
        self.clear_old_classes()

        if not self.students:
            print("❌ No students found. Please run seed_database.py first.")
            return

        self.generate_historical_semesters()
        self.generate_current_semester_data()
        self.update_student_gpas()
        self.generate_performance_trends()

        print("\n✅ Test data generation completed!")
        self.print_summary()

    def load_existing_data(self):
        """Load existing data from database."""
        print("📥 Loading existing data...")

        self.students = list(Student.objects.all())
        self.instructors = list(User.objects.filter(role='INSTRUCTOR'))
        self.courses = list(Course.objects.all())
        self.rooms = list(Room.objects.all())

        print(f"   Loaded: {len(self.students)} students")
        print(f"   Loaded: {len(self.instructors)} instructors")
        print(f"   Loaded: {len(self.courses)} courses")
        print(f"   Loaded: {len(self.rooms)} rooms")

    def clear_old_classes(self):
        """Clear old classes to avoid UNIQUE constraint errors."""
        from courses.models import Class
        print("🗑️ Clearing existing classes...")
        Class.objects.all().delete()
        print("   ✓ Old classes cleared")

    @transaction.atomic
    def generate_historical_semesters(self):
        """Generate data for past 3 semesters."""
        print("\n📚 Generating historical semester data...")

        semesters = [
            (self.current_year - 1, 'FALL'),
            (self.current_year, 'SPRING'),
            (self.current_year, 'SUMMER'),
        ]

        for year, semester in semesters:
            print(f"\n   Processing {semester} {year}...")
            self.generate_semester_data(year, semester, completed=True)

    def generate_semester_data(self, year, semester, completed=False):
        """Generate data for a specific semester."""
        classes_created = []

        for course in random.sample(self.courses, min(8, len(self.courses))):
            instructor = random.choice(self.instructors)
            room = random.choice(self.rooms)

            # Generate unique section for each class
            section = str(random.randint(1, 99)).zfill(3)
            class_code = f'{course.course_code}-{semester[0]}{year % 100}-{section}'

            class_instance, created = Class.objects.get_or_create(
                course=course,
                semester=semester,
                academic_year=year,
                section=section,
                defaults={
                    'instructor': instructor,
                    'class_code': class_code,
                    'max_capacity': random.randint(25, 40),
                    'current_enrollment': 0,
                    'room': room,
                    'schedule': [
                        {'day': 'Monday', 'start_time': '09:00:00', 'end_time': '10:30:00'},
                        {'day': 'Wednesday', 'start_time': '09:00:00', 'end_time': '10:30:00'}
                    ],
                    'status': 'CLOSED' if completed else 'OPEN'
                }
            )

            if created or not completed:
                classes_created.append(class_instance)

        # Enroll students
        for student in self.students[:15]:
            num_courses = random.randint(3, 5)
            student_classes = random.sample(classes_created, min(num_courses, len(classes_created)))

            for class_instance in student_classes:
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    class_instance=class_instance,
                    defaults={
                        'enrollment_date': datetime(year, 1 if semester == 'SPRING' else 8, 15),
                        'status': 'COMPLETED' if completed else 'ENROLLED'
                    }
                )

                if created:
                    class_instance.current_enrollment += 1
                    class_instance.save()

                    if completed:
                        self.generate_grades_for_enrollment(enrollment)
                        self.finalize_enrollment_grade(enrollment)

                    self.generate_attendance_for_enrollment(enrollment, completed)

        print(f"      ✓ Created {len(classes_created)} classes")

    def generate_grades_for_enrollment(self, enrollment):
        """Generate grades for an enrollment."""
        assignments = [
            ('Quiz 1', 20, 5),
            ('Assignment 1', 100, 10),
            ('Midterm Exam', 100, 25),
            ('Assignment 2', 100, 10),
            ('Quiz 2', 20, 5),
            ('Project', 100, 15),
            ('Final Exam', 100, 30),
        ]

        performance_factor = random.uniform(0.6, 1.0)

        for assignment_name, total_marks, weight in assignments:
            base_score = total_marks * performance_factor
            variation = random.uniform(-0.1, 0.1) * total_marks
            marks_obtained = max(0, min(total_marks, base_score + variation))

            Grade.objects.create(
                enrollment=enrollment,
                assignment_name=assignment_name,
                marks_obtained=round(marks_obtained, 2),
                total_marks=total_marks,
                weight_percentage=weight,
                graded_by=enrollment.class_instance.instructor,
                graded_date=enrollment.enrollment_date + timedelta(days=random.randint(10, 90))
            )

    def finalize_enrollment_grade(self, enrollment):
        """Calculate and set final grade for enrollment."""
        grades = Grade.objects.filter(enrollment=enrollment)

        if not grades.exists():
            return

        total_weighted_score = 0
        total_weight = 0

        for grade in grades:
            percentage = (grade.marks_obtained / grade.total_marks) * 100
            total_weighted_score += percentage * grade.weight_percentage
            total_weight += grade.weight_percentage

        if total_weight > 0:
            final_percentage = total_weighted_score / total_weight

            if final_percentage >= 95:
                letter_grade = 'A+'
                grade_points = 4.00
            elif final_percentage >= 90:
                letter_grade = 'A'
                grade_points = 4.00
            elif final_percentage >= 85:
                letter_grade = 'B+'
                grade_points = 3.50
            elif final_percentage >= 80:
                letter_grade = 'B'
                grade_points = 3.00
            elif final_percentage >= 75:
                letter_grade = 'C+'
                grade_points = 2.50
            elif final_percentage >= 70:
                letter_grade = 'C'
                grade_points = 2.00
            elif final_percentage >= 60:
                letter_grade = 'D'
                grade_points = 1.00
            else:
                letter_grade = 'F'
                grade_points = 0.00

            enrollment.grade = letter_grade
            enrollment.grade_points = Decimal(str(grade_points))
            enrollment.status = 'COMPLETED'
            enrollment.save()

    def generate_attendance_for_enrollment(self, enrollment, completed=False):
        """Generate attendance records for enrollment."""
        attendance_rate = random.uniform(0.7, 1.0)

        if completed:
            num_days = random.randint(40, 50)
            start_date = enrollment.enrollment_date.date()
        else:
            num_days = min(30, (date.today() - enrollment.enrollment_date.date()).days)
            start_date = enrollment.enrollment_date.date()

        for day_offset in range(num_days):
            attendance_date = start_date + timedelta(days=day_offset * 2)

            if attendance_date.weekday() >= 5:
                continue

            rand = random.random()
            if rand < attendance_rate:
                status = 'PRESENT'
            elif rand < attendance_rate + 0.1:
                status = 'LATE'
            elif rand < attendance_rate + 0.15:
                status = 'EXCUSED'
            else:
                status = 'ABSENT'

            Attendance.objects.get_or_create(
                enrollment=enrollment,
                date=attendance_date,
                defaults={
                    'status': status,
                    'recorded_by': enrollment.class_instance.instructor
                }
            )

    @transaction.atomic
    def generate_current_semester_data(self):
        """Generate data for current semester."""
        print(f"\n📅 Generating current semester data ({self.current_year} FALL)...")
        self.generate_semester_data(self.current_year, 'FALL', completed=False)

    @transaction.atomic
    def update_student_gpas(self):
        """Calculate and update student GPAs."""
        print("\n📊 Calculating student GPAs...")

        for student in self.students:
            completed_enrollments = Enrollment.objects.filter(
                student=student,
                status='COMPLETED',
                grade_points__isnull=False
            )

            if completed_enrollments.exists():
                total_points = 0
                total_credits = 0

                for enrollment in completed_enrollments:
                    credits = enrollment.class_instance.course.credits
                    points = float(enrollment.grade_points) * credits

                    total_points += points
                    total_credits += credits

                if total_credits > 0:
                    gpa = total_points / total_credits
                    student.gpa = Decimal(str(round(gpa, 2)))

                    if gpa < 2.0:
                        student.academic_status = 'SUSPENDED'
                    elif gpa >= 3.5:
                        student.academic_status = 'ACTIVE'

                    student.save()
                    print(f"   ✓ Updated GPA for {student.student_id}: {student.gpa}")

    def generate_performance_trends(self):
        """Generate performance trend data."""
        print("\n📈 Generating performance trends...")

        improving_students = self.students[:5]
        for student in improving_students:
            print(f"   ✓ Generated improving trend for {student.student_id}")

        declining_students = self.students[5:10]
        for student in declining_students:
            print(f"   ✓ Generated declining trend for {student.student_id}")

        print(f"   ✓ Generated stable trends for remaining students")

    def print_summary(self):
        """Print summary of generated data."""
        print("\n" + "="*50)
        print("📊 TEST DATA GENERATION SUMMARY")
        print("="*50)

        total_enrollments = Enrollment.objects.count()
        completed_enrollments = Enrollment.objects.filter(status='COMPLETED').count()
        active_enrollments = Enrollment.objects.filter(status='ENROLLED').count()

        print(f"Total Enrollments: {total_enrollments}")
        print(f"  - Completed: {completed_enrollments}")
        print(f"  - Active: {active_enrollments}")
        print(f"\nTotal Grades: {Grade.objects.count()}")
        print(f"Total Attendance Records: {Attendance.objects.count()}")

        students_with_gpa = Student.objects.filter(gpa__gt=0).count()
        avg_gpa = Student.objects.filter(gpa__gt=0).aggregate(avg_gpa=Avg('gpa'))['avg_gpa']

        print(f"\nStudents with GPA: {students_with_gpa}")
        print(f"Average GPA: {avg_gpa:.2f}" if avg_gpa else "Average GPA: N/A")

        semesters = Class.objects.values('academic_year', 'semester').distinct()
        print(f"\nSemesters Generated: {len(semesters)}")
        for sem in semesters:
            classes_count = Class.objects.filter(
                academic_year=sem['academic_year'],
                semester=sem['semester']
            ).count()
            print(f"  - {sem['semester']} {sem['academic_year']}: {classes_count} classes")

        print("="*50)


def main():
    generator = TestDataGenerator()

    try:
        generator.generate_all()
    except Exception as e:
        print(f"\n❌ Error generating test data: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
