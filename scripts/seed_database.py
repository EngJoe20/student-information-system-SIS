# ============================================================================
# scripts/seed_database.py
# ============================================================================
"""
Seed database with initial data for development/testing.

Usage:
    python scripts/seed_database.py
    
Or as Django management command (recommended):
    python manage.py seed_database
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sis_backend.settings.development')
django.setup()

from django.db import transaction
from accounts.models import User
from students.models import Student, Enrollment
from courses.models import Course, Class, Room, Exam
from attendance.models import Attendance
from grades.models import Grade
from notifications.models import Notification, Message, StudentRequest


class DatabaseSeeder:
    """Seed database with initial data."""
    
    def __init__(self):
        self.users = {}
        self.students = []
        self.courses = []
        self.classes = []
        self.rooms = []
        
    @transaction.atomic
    def seed_all(self):
        """Seed all data."""
        print("🌱 Starting database seeding...")
        
        # Clear existing data (optional)
        self.clear_data()
        
        # Seed in order of dependencies
        self.seed_users()
        self.seed_students()
        self.seed_rooms()
        self.seed_courses()
        self.seed_classes()
        self.seed_enrollments()
        self.seed_attendance()
        self.seed_grades()
        self.seed_exams()
        self.seed_notifications()
        self.seed_messages()
        self.seed_student_requests()
        
        print("\n✅ Database seeding completed successfully!")
        self.print_summary()
    
    def clear_data(self):
        """Clear existing data (optional - use with caution!)."""
        print("🗑️  Clearing existing data...")
        
        # Clear in reverse order of dependencies
        Grade.objects.all().delete()
        Attendance.objects.all().delete()
        Exam.objects.all().delete()
        Enrollment.objects.all().delete()
        Class.objects.all().delete()
        Course.objects.all().delete()
        Room.objects.all().delete()
        StudentRequest.objects.all().delete()
        Message.objects.all().delete()
        Notification.objects.all().delete()
        Student.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        
        print("   ✓ Existing data cleared")
    
    def seed_users(self):
        """Seed users with different roles."""
        print("\n👤 Seeding users...")
        
        users_data = [
            # Admin
            {
                'username': 'admin',
                'email': 'admin@sis.com',
                'password': 'Admin123!',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'ADMIN',
                'phone_number': '+1234567890'
            },
            # Registrars
            {
                'username': 'registrar1',
                'email': 'registrar1@sis.com',
                'password': 'Registrar123!',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'REGISTRAR',
                'phone_number': '+1234567891'
            },
            # Instructors
            {
                'username': 'instructor1',
                'email': 'instructor1@sis.com',
                'password': 'Instructor123!',
                'first_name': 'Dr. John',
                'last_name': 'Smith',
                'role': 'INSTRUCTOR',
                'phone_number': '+1234567892'
            },
            {
                'username': 'instructor2',
                'email': 'instructor2@sis.com',
                'password': 'Instructor123!',
                'first_name': 'Prof. Emily',
                'last_name': 'Davis',
                'role': 'INSTRUCTOR',
                'phone_number': '+1234567893'
            },
            {
                'username': 'instructor3',
                'email': 'instructor3@sis.com',
                'password': 'Instructor123!',
                'first_name': 'Dr. Michael',
                'last_name': 'Brown',
                'role': 'INSTRUCTOR',
                'phone_number': '+1234567894'
            },
        ]
        
        for user_data in users_data:
            password = user_data.pop('password')
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password(password)
                user.save()
                print(f"   ✓ Created {user.role}: {user.username}")
            
            self.users[user.role] = user
    
    def seed_students(self):
        """Seed student profiles."""
        print("\n🎓 Seeding students...")
        
        first_names = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 
                      'Robert', 'Lisa', 'James', 'Mary', 'Ahmed', 'Fatima']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
                     'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Ali', 'Hassan']
        
        for i in range(1, 21):  # Create 20 students
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"student{i}"
            
            # Create user
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@student.sis.com',
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'STUDENT',
                    'phone_number': f'+12345678{i:02d}'
                }
            )
            if created:
                user.set_password('Student123!')
                user.save()
            
            # Create student profile
            student, created = Student.objects.get_or_create(
                user=user,
                defaults={
                    'student_id': f'S2025{i:03d}',
                    'date_of_birth': date(2002 + (i % 5), (i % 12) + 1, (i % 28) + 1),
                    'gender': random.choice(['MALE', 'FEMALE', 'OTHER']),
                    'address': f'{100 + i} Main Street',
                    'city': random.choice(['Cairo', 'Alexandria', 'Giza', 'New York']),
                    'state': random.choice(['Cairo', 'Alexandria', 'NY', 'CA']),
                    'postal_code': f'{12345 + i}',
                    'country': random.choice(['Egypt', 'USA']),
                    'emergency_contact_name': f'{first_name} {last_name} Sr.',
                    'emergency_contact_phone': f'+19876543{i:02d}',
                    'enrollment_date': date(2025, 9, 1),
                    'academic_status': 'ACTIVE',
                    'gpa': round(random.uniform(2.5, 4.0), 2)
                }
            )
            
            if created:
                self.students.append(student)
                print(f"   ✓ Created student: {student.student_id} - {user.full_name}")
    
    def seed_rooms(self):
        """Seed classroom and lab rooms."""
        print("\n🏫 Seeding rooms...")
        
        buildings = ['Main Building', 'Science Building', 'Engineering Hall', 'Arts Building']
        room_types = ['CLASSROOM', 'LAB', 'LECTURE_HALL', 'SEMINAR']
        
        room_num = 101
        for building in buildings:
            for i in range(5):  # 5 rooms per building
                room, created = Room.objects.get_or_create(
                    room_number=f'{room_num}',
                    building=building,
                    defaults={
                        'capacity': random.choice([30, 40, 50, 60, 100]),
                        'room_type': random.choice(room_types),
                        'equipment': ['Projector', 'Whiteboard', 'Computer'],
                        'is_available': True
                    }
                )
                if created:
                    self.rooms.append(room)
                    print(f"   ✓ Created room: {building} - {room_num}")
                room_num += 1
    
    def seed_courses(self):
        """Seed course catalog."""
        print("\n📚 Seeding courses...")
        
        courses_data = [
            # Computer Science
            ('CS101', 'Introduction to Computer Science', 'Computer Science', 3, ''),
            ('CS201', 'Data Structures and Algorithms', 'Computer Science', 4, 'CS101'),
            ('CS301', 'Database Management Systems', 'Computer Science', 3, 'CS201'),
            ('CS401', 'Software Engineering', 'Computer Science', 4, 'CS301'),
            
            # Mathematics
            ('MATH101', 'Calculus I', 'Mathematics', 4, ''),
            ('MATH201', 'Calculus II', 'Mathematics', 4, 'MATH101'),
            ('MATH301', 'Linear Algebra', 'Mathematics', 3, 'MATH201'),
            
            # Physics
            ('PHYS101', 'General Physics I', 'Physics', 4, ''),
            ('PHYS201', 'General Physics II', 'Physics', 4, 'PHYS101'),
            
            # English
            ('ENG101', 'English Composition', 'English', 3, ''),
            ('ENG201', 'Technical Writing', 'English', 3, 'ENG101'),
            
            # Business
            ('BUS101', 'Introduction to Business', 'Business', 3, ''),
            ('BUS201', 'Marketing Principles', 'Business', 3, 'BUS101'),
        ]
        
        course_objects = {}
        for code, name, dept, credits, prereq_code in courses_data:
            course, created = Course.objects.get_or_create(
                course_code=code,
                defaults={
                    'course_name': name,
                    'description': f'This course covers {name.lower()}',
                    'credits': credits,
                    'department': dept,
                    'is_active': True
                }
            )
            course_objects[code] = course
            if created:
                self.courses.append(course)
                print(f"   ✓ Created course: {code} - {name}")
        
        # Add prerequisites
        for code, name, dept, credits, prereq_code in courses_data:
            if prereq_code:
                course = course_objects[code]
                prereq = course_objects[prereq_code]
                course.prerequisites.add(prereq)
    
    def seed_classes(self):
        """Seed class sections."""
        print("\n📅 Seeding classes...")
        
        current_year = datetime.now().year
        semesters = ['FALL', 'SPRING']
        instructors = [self.users.get('INSTRUCTOR')]
        
        # Get additional instructors
        additional_instructors = User.objects.filter(role='INSTRUCTOR').exclude(
            username='instructor1'
        )[:2]
        instructors.extend(additional_instructors)
        
        for course in self.courses[:10]:  # First 10 courses
            for semester in semesters:
                for section_num in range(1, 3):  # 2 sections per course
                    instructor = random.choice(instructors)
                    room = random.choice(self.rooms)
                    
                    schedule = [
                        {
                            'day': random.choice(['Monday', 'Wednesday', 'Friday']),
                            'start_time': '09:00:00',
                            'end_time': '10:30:00'
                        },
                        {
                            'day': random.choice(['Tuesday', 'Thursday']),
                            'start_time': '14:00:00',
                            'end_time': '15:30:00'
                        }
                    ]
                    
                    class_obj, created = Class.objects.get_or_create(
                        class_code=f'{course.course_code}-{section_num:03d}',
                        defaults={
                            'course': course,
                            'instructor': instructor,
                            'section': f'{section_num:03d}',
                            'semester': semester,
                            'academic_year': current_year,
                            'max_capacity': room.capacity,
                            'current_enrollment': 0,
                            'room': room,
                            'schedule': schedule,
                            'status': 'OPEN'
                        }
                    )
                    
                    if created:
                        self.classes.append(class_obj)
                        print(f"   ✓ Created class: {class_obj.class_code} ({semester})")
    
    def seed_enrollments(self):
        """Seed student enrollments."""
        print("\n✍️  Seeding enrollments...")
        
        enrolled_count = 0
        for student in self.students:
            # Enroll each student in 3-5 random classes
            num_classes = random.randint(3, 5)
            available_classes = random.sample(self.classes, num_classes)
            
            for class_obj in available_classes:
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    class_instance=class_obj,
                    defaults={
                        'enrollment_date': datetime.now(),
                        'status': 'ENROLLED'
                    }
                )
                
                if created:
                    # Update class enrollment count
                    class_obj.current_enrollment += 1
                    class_obj.save()
                    enrolled_count += 1
        
        print(f"   ✓ Created {enrolled_count} enrollments")
    
    def seed_attendance(self):
        """Seed attendance records."""
        print("\n✅ Seeding attendance records...")
        
        enrollments = Enrollment.objects.filter(status='ENROLLED')
        statuses = ['PRESENT', 'PRESENT', 'PRESENT', 'ABSENT', 'LATE']
        
        # Create attendance for last 30 days
        attendance_count = 0
        for enrollment in enrollments[:50]:  # First 50 enrollments
            for day_offset in range(20):  # 20 days of attendance
                attendance_date = date.today() - timedelta(days=day_offset)
                
                attendance, created = Attendance.objects.get_or_create(
                    enrollment=enrollment,
                    date=attendance_date,
                    defaults={
                        'status': random.choice(statuses),
                        'recorded_by': enrollment.class_instance.instructor
                    }
                )
                
                if created:
                    attendance_count += 1
        
        print(f"   ✓ Created {attendance_count} attendance records")
    
    def seed_grades(self):
        """Seed grade records."""
        print("\n📊 Seeding grades...")
        
        enrollments = Enrollment.objects.filter(status='ENROLLED')
        assignments = [
            ('Assignment 1', 100, 20),
            ('Midterm Exam', 100, 30),
            ('Assignment 2', 100, 20),
            ('Final Exam', 100, 30)
        ]
        
        grade_count = 0
        for enrollment in enrollments[:50]:
            for assignment_name, total_marks, weight in assignments:
                marks_obtained = random.uniform(60, 100)
                
                grade, created = Grade.objects.get_or_create(
                    enrollment=enrollment,
                    assignment_name=assignment_name,
                    defaults={
                        'marks_obtained': round(marks_obtained, 2),
                        'total_marks': total_marks,
                        'weight_percentage': weight,
                        'graded_by': enrollment.class_instance.instructor,
                        'graded_date': datetime.now()
                    }
                )
                
                if created:
                    grade_count += 1
        
        print(f"   ✓ Created {grade_count} grade records")
    
    def seed_exams(self):
        """Seed exam schedules."""
        print("\n📝 Seeding exams...")
        
        exam_types = ['MIDTERM', 'FINAL', 'QUIZ']
        exam_count = 0
        
        for class_obj in self.classes[:10]:
            for exam_type in ['MIDTERM', 'FINAL']:
                days_ahead = 30 if exam_type == 'MIDTERM' else 60
                exam_date = datetime.now() + timedelta(days=days_ahead)
                
                exam, created = Exam.objects.get_or_create(
                    class_instance=class_obj,
                    exam_type=exam_type,
                    defaults={
                        'exam_date': exam_date,
                        'duration_minutes': 120 if exam_type == 'FINAL' else 90,
                        'room': class_obj.room,
                        'total_marks': 100,
                        'instructions': f'{exam_type} examination instructions'
                    }
                )
                
                if created:
                    exam_count += 1
        
        print(f"   ✓ Created {exam_count} exam schedules")
    
    def seed_notifications(self):
        """Seed notifications."""
        print("\n🔔 Seeding notifications...")
        
        notification_types = ['GRADE', 'ATTENDANCE', 'ENROLLMENT', 'ANNOUNCEMENT', 'SYSTEM']
        notification_count = 0
        
        students_users = User.objects.filter(role='STUDENT')[:10]
        
        for user in students_users:
            for i in range(3):
                notif_type = random.choice(notification_types)
                notification, created = Notification.objects.get_or_create(
                    recipient=user,
                    title=f'{notif_type.title()} Notification',
                    defaults={
                        'notification_type': notif_type,
                        'message': f'This is a test {notif_type.lower()} notification',
                        'is_read': random.choice([True, False]),
                        'priority': random.choice(['LOW', 'MEDIUM', 'HIGH'])
                    }
                )
                
                if created:
                    notification_count += 1
        
        print(f"   ✓ Created {notification_count} notifications")
    
    def seed_messages(self):
        """Seed internal messages."""
        print("\n💬 Seeding messages...")
        
        students_users = list(User.objects.filter(role='STUDENT')[:5])
        instructors = list(User.objects.filter(role='INSTRUCTOR')[:3])
        
        message_count = 0
        for i in range(10):
            sender = random.choice(students_users + instructors)
            recipient = random.choice(students_users + instructors)
            
            if sender != recipient:
                message, created = Message.objects.get_or_create(
                    sender=sender,
                    recipient=recipient,
                    subject=f'Test Message {i+1}',
                    defaults={
                        'body': f'This is test message body content {i+1}',
                        'is_read': random.choice([True, False])
                    }
                )
                
                if created:
                    message_count += 1
        
        print(f"   ✓ Created {message_count} messages")
    
    def seed_student_requests(self):
        """Seed student service requests."""
        print("\n📋 Seeding student requests...")
        
        request_types = ['TRANSCRIPT', 'CERTIFICATE', 'COURSE_ADD', 'COURSE_DROP', 'GRADE_APPEAL']
        statuses = ['PENDING', 'IN_PROGRESS', 'APPROVED', 'REJECTED']
        
        request_count = 0
        for student in self.students[:10]:
            for i in range(2):
                request_type = random.choice(request_types)
                request, created = StudentRequest.objects.get_or_create(
                    student=student,
                    request_type=request_type,
                    defaults={
                        'subject': f'{request_type.replace("_", " ").title()} Request',
                        'description': f'Request for {request_type.lower().replace("_", " ")}',
                        'status': random.choice(statuses)
                    }
                )
                
                if created:
                    request_count += 1
        
        print(f"   ✓ Created {request_count} student requests")
    
    def print_summary(self):
        """Print summary of seeded data."""
        print("\n" + "="*50)
        print("📊 DATABASE SEEDING SUMMARY")
        print("="*50)
        print(f"Users: {User.objects.count()}")
        print(f"  - Admins: {User.objects.filter(role='ADMIN').count()}")
        print(f"  - Registrars: {User.objects.filter(role='REGISTRAR').count()}")
        print(f"  - Instructors: {User.objects.filter(role='INSTRUCTOR').count()}")
        print(f"  - Students: {User.objects.filter(role='STUDENT').count()}")
        print(f"\nStudents: {Student.objects.count()}")
        print(f"Courses: {Course.objects.count()}")
        print(f"Classes: {Class.objects.count()}")
        print(f"Rooms: {Room.objects.count()}")
        print(f"Enrollments: {Enrollment.objects.count()}")
        print(f"Attendance Records: {Attendance.objects.count()}")
        print(f"Grades: {Grade.objects.count()}")
        print(f"Exams: {Exam.objects.count()}")
        print(f"Notifications: {Notification.objects.count()}")
        print(f"Messages: {Message.objects.count()}")
        print(f"Student Requests: {StudentRequest.objects.count()}")
        print("="*50)
        print("\n📝 Test Accounts Created:")
        print("="*50)
        print("Admin:")
        print("  Username: admin")
        print("  Password: Admin123!")
        print("\nInstructor:")
        print("  Username: instructor1")
        print("  Password: Instructor123!")
        print("\nStudent:")
        print("  Username: student1")
        print("  Password: Student123!")
        print("="*50)


def main():
    """Main execution function."""
    seeder = DatabaseSeeder()
    
    try:
        seeder.seed_all()
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()