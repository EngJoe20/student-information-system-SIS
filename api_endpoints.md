# Student Information System - API Endpoints Documentation

**Base URL:** `http://localhost:8000/api/v1/`

**Authentication:** JWT Bearer Token (except login/register endpoints)

**Response Format:** All responses follow standard format:
```json
{
  "status": "success|error|2fa_required",
  "message": "Optional message",
  "data": { /* Response data */ },
  "code": "Error code (if error)",
  "errors": { /* Validation errors */ },
  "timestamp": "ISO 8601 timestamp"
}
```

---

## 🔐 Authentication Endpoints (`/api/v1/auth/`)

### 1. Login
- **Method:** `POST`
- **URL:** `/api/v1/auth/login/`
- **Permissions:** Public
- **Request Body:**
```json
{
  "username": "student123",
  "password": "password123"
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "uuid",
      "username": "student123",
      "email": "student@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "role": "STUDENT",
      "is_active": true,
      "is_2fa_enabled": false,
      "phone_number": "+1234567890",
      "created_at": "2025-01-01T00:00:00Z",
      "last_login": "2025-01-15T10:30:00Z"
    },
    "requires_2fa": false
  }
}
```
- **2FA Required Response (202):**
```json
{
  "status": "2fa_required",
  "message": "Please provide OTP code",
  "temp_token": "temporary_token_string"
}
```

### 2. Verify 2FA Login
- **Method:** `POST`
- **URL:** `/api/v1/auth/verify-2fa/`
- **Permissions:** Public
- **Request Body:**
```json
{
  "temp_token": "temporary_token_string",
  "otp_code": "123456"
}
```
- **Success Response (200):** Same as login success response

### 3. Logout
- **Method:** `POST`
- **URL:** `/api/v1/auth/logout/`
- **Permissions:** Authenticated
- **Request Body:**
```json
{
  "refresh_token": "refresh_token_string"
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "Successfully logged out"
}
```

### 4. Refresh Token
- **Method:** `POST`
- **URL:** `/api/v1/auth/refresh/`
- **Permissions:** Public
- **Request Body:**
```json
{
  "refresh_token": "refresh_token_string"
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "access_token": "new_access_token",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

### 5. Password Reset Request
- **Method:** `POST`
- **URL:** `/api/v1/auth/password-reset/`
- **Permissions:** Public
- **Request Body:**
```json
{
  "email": "user@example.com"
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "Password reset instructions sent to email"
}
```

### 6. Password Reset Confirm
- **Method:** `POST`
- **URL:** `/api/v1/auth/password-reset-confirm/`
- **Permissions:** Public
- **Request Body:**
```json
{
  "token": "reset_token_string",
  "new_password": "newPassword123",
  "confirm_password": "newPassword123"
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "Password has been reset successfully"
}
```

---

## 👥 User Management Endpoints (`/api/v1/users/`)

### 1. List Users
- **Method:** `GET`
- **URL:** `/api/v1/users/`
- **Permissions:** Admin
- **Query Parameters:**
  - `role` (optional): Filter by role (STUDENT, ADMIN, REGISTRAR, INSTRUCTOR)
  - `is_active` (optional): Filter by active status (true/false)
  - `search` (optional): Search by username, email, first_name, last_name
  - `page` (optional): Page number for pagination
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "count": 100,
    "next": "http://localhost:8000/api/v1/users/?page=2",
    "previous": null,
    "results": [
      {
        "id": "uuid",
        "username": "student123",
        "email": "student@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "role": "STUDENT",
        "is_active": true,
        "is_2fa_enabled": false,
        "phone_number": "+1234567890",
        "created_at": "2025-01-01T00:00:00Z",
        "last_login": "2025-01-15T10:30:00Z"
      }
    ]
  }
}
```

### 2. Create User
- **Method:** `POST`
- **URL:** `/api/v1/users/`
- **Permissions:** Admin
- **Request Body:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "SecurePassword123",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "STUDENT",
  "phone_number": "+1234567890",
  "is_active": true
}
```
- **Success Response (201):**
```json
{
  "status": "success",
  "message": "User created successfully",
  "data": {
    "id": "uuid",
    "username": "newuser",
    "email": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "full_name": "Jane Smith",
    "role": "STUDENT",
    "is_active": true,
    "is_2fa_enabled": false,
    "phone_number": "+1234567890",
    "created_at": "2025-01-15T10:30:00Z",
    "last_login": null
  }
}
```

### 3. Get User Details
- **Method:** `GET`
- **URL:** `/api/v1/users/{id}/`
- **Permissions:** Authenticated (own profile or Admin)
- **Success Response (200):** Same as user object in list

### 4. Update User
- **Method:** `PUT` / `PATCH`
- **URL:** `/api/v1/users/{id}/`
- **Permissions:** Admin
- **Request Body:**
```json
{
  "email": "updated@example.com",
  "first_name": "Updated",
  "last_name": "Name",
  "role": "INSTRUCTOR",
  "phone_number": "+9876543210",
  "is_active": true
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "User updated successfully",
  "data": { /* Updated user object */ }
}
```

### 5. Delete User
- **Method:** `DELETE`
- **URL:** `/api/v1/users/{id}/`
- **Permissions:** Admin
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "User deleted successfully"
}
```

### 6. Get Current User
- **Method:** `GET`
- **URL:** `/api/v1/users/me/`
- **Permissions:** Authenticated
- **Success Response (200):** User object

### 7. Assign Role
- **Method:** `POST`
- **URL:** `/api/v1/users/{id}/assign-role/`
- **Permissions:** Admin
- **Request Body:**
```json
{
  "role": "INSTRUCTOR"
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "Role assigned successfully",
  "data": { /* Updated user object */ }
}
```

### 8. Enable 2FA
- **Method:** `POST`
- **URL:** `/api/v1/users/enable-2fa/`
- **Permissions:** Authenticated
- **Request Body:** `{}`
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "otp_secret": "base32_secret",
    "qr_code": "base64_encoded_qr_image",
    "message": "Scan QR code with authenticator app and verify"
  }
}
```

### 9. Verify 2FA Setup
- **Method:** `POST`
- **URL:** `/api/v1/users/verify-2fa-setup/`
- **Permissions:** Authenticated
- **Request Body:**
```json
{
  "otp_secret": "base32_secret",
  "otp_code": "123456"
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "2FA enabled successfully"
}
```

### 10. Disable 2FA
- **Method:** `POST`
- **URL:** `/api/v1/users/disable-2fa/`
- **Permissions:** Authenticated
- **Request Body:** `{}`
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "2FA disabled successfully"
}
```

---

## 🎓 Student Management Endpoints (`/api/v1/students/`)

### 1. List Students
- **Method:** `GET`
- **URL:** `/api/v1/students/`
- **Permissions:** Authenticated (Students see only themselves, Admin/Registrar see all)
- **Query Parameters:**
  - `academic_status` (optional): ACTIVE, SUSPENDED, GRADUATED, WITHDRAWN
  - `search` (optional): Search by student_id, name, email
  - `order_by` (optional): Sort field (default: -created_at)
  - `page` (optional): Page number
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "count": 50,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "uuid",
        "student_id": "STU001",
        "full_name": "John Doe",
        "email": "john@example.com",
        "academic_status": "ACTIVE",
        "gpa": 3.75,
        "enrollment_date": "2023-09-01"
      }
    ]
  }
}
```

### 2. Create Student
- **Method:** `POST`
- **URL:** `/api/v1/students/`
- **Permissions:** Admin, Registrar
- **Request Body:**
```json
{
  "user": {
    "username": "student123",
    "email": "student@example.com",
    "password": "SecurePassword123",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890"
  },
  "student_id": "STU001",
  "date_of_birth": "2000-01-15",
  "gender": "MALE",
  "address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "USA",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+1234567891",
  "enrollment_date": "2023-09-01"
}
```
- **Success Response (201):**
```json
{
  "status": "success",
  "message": "Student profile created successfully",
  "data": {
    "id": "uuid",
    "user": { /* User object */ },
    "full_name": "John Doe",
    "student_id": "STU001",
    "date_of_birth": "2000-01-15",
    "gender": "MALE",
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA",
    "emergency_contact_name": "Jane Doe",
    "emergency_contact_phone": "+1234567891",
    "enrollment_date": "2023-09-01",
    "graduation_date": null,
    "academic_status": "ACTIVE",
    "gpa": 0.00,
    "profile_picture": null,
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  }
}
```

### 3. Get Student Details
- **Method:** `GET`
- **URL:** `/api/v1/students/{id}/`
- **Permissions:** Authenticated (own profile or Admin/Registrar)
- **Success Response (200):** Full student object

### 4. Update Student
- **Method:** `PUT` / `PATCH`
- **URL:** `/api/v1/students/{id}/`
- **Permissions:** Admin, Registrar
- **Request Body:**
```json
{
  "address": "456 New St",
  "city": "Boston",
  "state": "MA",
  "postal_code": "02101",
  "country": "USA",
  "emergency_contact_name": "Updated Contact",
  "emergency_contact_phone": "+1234567892",
  "phone_number": "+1234567893",
  "academic_status": "ACTIVE",
  "profile_picture": "file_upload",
  "graduation_date": null
}
```
- **Success Response (200):** Updated student object

### 5. Delete Student
- **Method:** `DELETE`
- **URL:** `/api/v1/students/{id}/`
- **Permissions:** Admin, Registrar
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "Student deleted successfully"
}
```

### 6. Get Student Enrollments
- **Method:** `GET`
- **URL:** `/api/v1/students/{id}/enrollments/`
- **Permissions:** Authenticated (own data or Admin/Registrar)
- **Query Parameters:**
  - `semester` (optional): FALL, SPRING, SUMMER
  - `academic_year` (optional): Year number
  - `status` (optional): ENROLLED, DROPPED, COMPLETED, FAILED
- **Success Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "student": "uuid",
      "student_name": "John Doe",
      "student_id": "STU001",
      "class_instance": "uuid",
      "class_code": "CS101-A",
      "course_code": "CS101",
      "course_name": "Introduction to Computer Science",
      "credits": 3,
      "instructor_name": "Dr. Smith",
      "semester": "FALL",
      "academic_year": 2023,
      "enrollment_date": "2023-09-01T10:00:00Z",
      "status": "ENROLLED",
      "grade": null,
      "grade_points": null,
      "midterm_grade": null,
      "final_grade": null,
      "created_at": "2023-09-01T10:00:00Z"
    }
  ]
}
```

### 7. Get Student Attendance
- **Method:** `GET`
- **URL:** `/api/v1/students/{id}/attendance/`
- **Permissions:** Authenticated (own data or Admin/Instructor)
- **Query Parameters:**
  - `semester` (optional): FALL, SPRING, SUMMER
  - `academic_year` (optional): Year number
- **Success Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "course": "Introduction to Computer Science",
      "date": "2025-01-15",
      "status": "PRESENT"
    }
  ]
}
```

### 8. Get Student Grades
- **Method:** `GET`
- **URL:** `/api/v1/students/{id}/grades/`
- **Permissions:** Authenticated (own data or Admin/Instructor)
- **Query Parameters:**
  - `semester` (optional): FALL, SPRING, SUMMER
  - `academic_year` (optional): Year number
- **Success Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "course": "Introduction to Computer Science",
      "grade": "A",
      "status": "COMPLETED"
    }
  ]
}
```
```

### 9. Get Student Transcript
- **Method:** `GET`
- **URL:** `/api/v1/students/{id}/transcript/`
- **Permissions:** Authenticated (own data or Admin/Registrar)
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "student": "STU001",
    "gpa": 3.75,
    "courses": [
      {
        "course": "Introduction to Computer Science",
        "credits": 3,
        "grade": "A",
        "grade_point": 4.00
      }
    ]
  }
}
```

---

## 📚 Enrollment Endpoints (`/api/v1/enrollments/`)

### 1. List Enrollments
- **Method:** `GET`
- **URL:** `/api/v1/enrollments/`
- **Permissions:** Authenticated (Students see own, Instructors see their classes, Admin/Registrar see all)
- **Query Parameters:**
  - `student_id` (optional): Filter by student
  - `class_id` (optional): Filter by class
  - `status` (optional): ENROLLED, DROPPED, COMPLETED, FAILED
  - `page` (optional): Page number
- **Success Response (200):** Paginated enrollment list

### 2. Create Enrollment
- **Method:** `POST`
- **URL:** `/api/v1/enrollments/`
- **Permissions:** Authenticated (Students can enroll themselves, Admin/Registrar can enroll anyone)
- **Request Body:**
```json
{
  "student": "student_uuid",
  "class_instance": "class_uuid"
}
```
- **Success Response (201):**
```json
{
  "status": "success",
  "message": "Student enrolled successfully",
  "data": { /* Enrollment object */ }
}
```
- **Error Responses:**
  - `400`: Class full, prerequisites not met, schedule conflict
  - `403`: Student trying to enroll someone else

### 3. Get Enrollment Details
- **Method:** `GET`
- **URL:** `/api/v1/enrollments/{id}/`
- **Permissions:** Authenticated (own data or Admin/Registrar/Instructor)
- **Success Response (200):** Enrollment object

### 4. Drop Enrollment
- **Method:** `DELETE`
- **URL:** `/api/v1/enrollments/{id}/`
- **Permissions:** Authenticated (own enrollment or Admin/Registrar)
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "Enrollment dropped successfully",
  "data": { /* Updated enrollment object */ }
}
```
- **Error Response (400):** Cannot drop completed or failed enrollment

---

## 📖 Course Management Endpoints (`/api/v1/courses/`)

### 1. List Courses
- **Method:** `GET`
- **URL:** `/api/v1/courses/`
- **Permissions:** Authenticated (read-only for all, write for Admin)
- **Query Parameters:**
  - `department` (optional): Filter by department
  - `is_active` (optional): true/false
  - `search` (optional): Search by course_code, course_name, description
  - `page` (optional): Page number
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "count": 50,
    "results": [
      {
        "id": "uuid",
        "course_code": "CS101",
        "course_name": "Introduction to Computer Science",
        "credits": 3,
        "department": "Computer Science",
        "is_active": true,
        "prerequisites_count": 0
      }
    ]
  }
}
```

### 2. Create Course
- **Method:** `POST`
- **URL:** `/api/v1/courses/`
- **Permissions:** Admin
- **Request Body:**
```json
{
  "course_code": "CS101",
  "course_name": "Introduction to Computer Science",
  "description": "Basic programming concepts",
  "credits": 3,
  "department": "Computer Science",
  "prerequisite_ids": ["prerequisite_course_uuid"],
  "is_active": true
}
```
- **Success Response (201):** Course object

### 3. Get Course Details
- **Method:** `GET`
- **URL:** `/api/v1/courses/{id}/`
- **Permissions:** Authenticated
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "course_code": "CS101",
    "course_name": "Introduction to Computer Science",
    "description": "Basic programming concepts",
    "credits": 3,
    "department": "Computer Science",
    "prerequisites": [
      {
        "id": "uuid",
        "course_code": "CS100",
        "course_name": "Programming Fundamentals"
      }
    ],
    "prerequisites_count": 1,
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
    "active_classes": [ /* Class objects */ ]
  }
}
```

### 4. Update Course
- **Method:** `PUT` / `PATCH`
- **URL:** `/api/v1/courses/{id}/`
- **Permissions:** Admin
- **Request Body:**
```json
{
  "course_name": "Updated Course Name",
  "description": "Updated description",
  "credits": 4,
  "department": "Computer Science",
  "prerequisite_ids": ["uuid1", "uuid2"],
  "is_active": true
}
```
- **Success Response (200):** Updated course object

### 5. Delete Course
- **Method:** `DELETE`
- **URL:** `/api/v1/courses/{id}/`
- **Permissions:** Admin
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "Course deleted successfully"
}
```
- **Error Response (400):** Cannot delete course with active classes

---

## 🏫 Class Management Endpoints (`/api/v1/classes/`)

### 1. List Classes
- **Method:** `GET`
- **URL:** `/api/v1/classes/`
- **Permissions:** Authenticated
- **Query Parameters:**
  - `course_id` (optional): Filter by course
  - `instructor_id` (optional): Filter by instructor
  - `semester` (optional): FALL, SPRING, SUMMER
  - `academic_year` (optional): Year number
  - `status` (optional): OPEN, CLOSED, CANCELLED
  - `page` (optional): Page number
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "count": 20,
    "results": [
      {
        "id": "uuid",
        "class_code": "CS101-A",
        "course_code": "CS101",
        "course_name": "Introduction to Computer Science",
        "credits": 3,
        "section": "A",
        "instructor_name": "Dr. Smith",
        "semester": "FALL",
        "academic_year": 2023,
        "max_capacity": 30,
        "current_enrollment": 25,
        "available_seats": 5,
        "status": "OPEN"
      }
    ]
  }
}
```

### 2. Create Class
- **Method:** `POST`
- **URL:** `/api/v1/classes/`
- **Permissions:** Admin, Registrar
- **Request Body:**
```json
{
  "course": "course_uuid",
  "instructor": "instructor_uuid",
  "class_code": "CS101-A",
  "section": "A",
  "semester": "FALL",
  "academic_year": 2023,
  "max_capacity": 30,
  "room": "room_uuid",
  "schedule": [
    {
      "day": "MONDAY",
      "start_time": "09:00:00",
      "end_time": "10:30:00"
    },
    {
      "day": "WEDNESDAY",
      "start_time": "09:00:00",
      "end_time": "10:30:00"
    }
  ]
}
```
- **Success Response (201):** Class object

### 3. Get Class Details
- **Method:** `GET`
- **URL:** `/api/v1/classes/{id}/`
- **Permissions:** Authenticated
- **Success Response (200):** Full class object with course, instructor, room details

### 4. Update Class
- **Method:** `PUT` / `PATCH`
- **URL:** `/api/v1/classes/{id}/`
- **Permissions:** Admin, Registrar
- **Request Body:**
```json
{
  "instructor": "new_instructor_uuid",
  "section": "B",
  "max_capacity": 35,
  "room": "new_room_uuid",
  "schedule": [ /* Updated schedule */ ],
  "status": "CLOSED"
}
```
- **Success Response (200):** Updated class object

### 5. Get Class Timetable
- **Method:** `GET`
- **URL:** `/api/v1/classes/timetable/`
- **Permissions:** Authenticated
- **Query Parameters:**
  - `semester` (required): FALL, SPRING, SUMMER
  - `academic_year` (required): Year number
  - `student_id` (optional): Filter by student enrollments
  - `instructor_id` (optional): Filter by instructor
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "semester": "FALL",
    "academic_year": 2023,
    "schedule": [
      {
        "day": "MONDAY",
        "time_slots": [
          {
            "start_time": "09:00:00",
            "end_time": "10:30:00",
            "class": { /* Class object */ }
          }
        ]
      }
    ]
  }
}
```

### 6. Get Class Attendance
- **Method:** `GET`
- **URL:** `/api/v1/classes/{id}/attendance/`
- **Permissions:** Authenticated (Instructor for own classes, Admin/Registrar for all)
- **Query Parameters:**
  - `date` (optional): Filter by date (YYYY-MM-DD)
  - `status` (optional): PRESENT, ABSENT, LATE, EXCUSED
- **Success Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "enrollment": "uuid",
      "student_name": "John Doe",
      "student_id": "STU001",
      "class_code": "CS101-A",
      "course_name": "Introduction to Computer Science",
      "date": "2025-01-15",
      "status": "PRESENT",
      "notes": "",
      "recorded_by_name": "Dr. Smith",
      "created_at": "2025-01-15T09:00:00Z",
      "updated_at": "2025-01-15T09:00:00Z"
    }
  ]
}
```

### 7. Get Class Roster
- **Method:** `GET`
- **URL:** `/api/v1/classes/{id}/roster/`
- **Permissions:** Authenticated (Instructor for own classes, Admin/Registrar for all)
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "class": "uuid",
    "count": 25,
    "students": [
      {
        "id": "uuid",
        "student_id": "STU001",
        "full_name": "John Doe",
        "email": "john@example.com",
        "academic_status": "ACTIVE",
        "gpa": 3.75,
        "enrollment_date": "2023-09-01"
      }
    ]
  }
}
```

---

## 📝 Attendance Endpoints (`/api/v1/attendance/`)

### 1. List Attendance Records
- **Method:** `GET`
- **URL:** `/api/v1/attendance/`
- **Permissions:** Authenticated (Students see own, Instructors see their classes, Admin see all)
- **Query Parameters:**
  - `enrollment_id` (optional): Filter by enrollment
  - `date` (optional): Filter by date
  - `status` (optional): PRESENT, ABSENT, LATE, EXCUSED
  - `page` (optional): Page number
- **Success Response (200):** Paginated attendance records

### 2. Record Attendance
- **Method:** `POST`
- **URL:** `/api/v1/attendance/`
- **Permissions:** Admin, Instructor (for own classes)
- **Request Body:**
```json
{
  "enrollment": "enrollment_uuid",
  "date": "2025-01-15",
  "status": "PRESENT",
  "notes": "On time"
}
```
- **Success Response (201):**
```json
{
  "status": "success",
  "message": "Attendance recorded successfully",
  "data": { /* Attendance object */ }
}
```

### 3. Update Attendance
- **Method:** `PUT` / `PATCH`
- **URL:** `/api/v1/attendance/{id}/`
- **Permissions:** Admin, Instructor (for own classes)
- **Request Body:**
```json
{
  "status": "LATE",
  "notes": "Arrived 10 minutes late"
}
```
- **Success Response (200):** Updated attendance object

### 4. Bulk Record Attendance
- **Method:** `POST`
- **URL:** `/api/v1/attendance/bulk-record/`
- **Permissions:** Admin, Instructor (for own classes)
- **Request Body:**
```json
{
  "class_id": "class_uuid",
  "date": "2025-01-15",
  "attendance_records": [
    {
      "enrollment_id": "enrollment_uuid1",
      "status": "PRESENT",
      "notes": ""
    },
    {
      "enrollment_id": "enrollment_uuid2",
      "status": "ABSENT",
      "notes": "Excused absence"
    }
  ]
}
```
- **Success Response (201):**
```json
{
  "status": "success",
  "message": "Attendance recorded successfully",
  "data": {
    "class_id": "uuid",
    "date": "2025-01-15",
    "total_records": 25,
    "recorded_by": "Dr. Smith"
  }
}
```

### 5. Get Student Attendance
- **Method:** `GET`
- **URL:** `/api/v1/attendance/student/{student_id}/`
- **Permissions:** Authenticated (own data or Admin/Instructor)
- **Query Parameters:**
  - `class_id` (optional): Filter by class
  - `start_date` (optional): Start date filter
  - `end_date` (optional): End date filter
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "student": {
      "id": "uuid",
      "student_id": "STU001",
      "name": "John Doe"
    },
    "attendance_summary": {
      "total_days": 30,
      "present": 25,
      "absent": 3,
      "late": 2,
      "excused": 0,
      "attendance_percentage": 83.33
    },
    "records": [ /* Attendance records */ ]
  }
}
```

### 6. Get Class Attendance
- **Method:** `GET`
- **URL:** `/api/v1/attendance/class/{class_id}/`
- **Permissions:** Authenticated (Instructor for own classes, Admin/Registrar for all)
- **Query Parameters:**
  - `date` (required): Date (YYYY-MM-DD)
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "class": {
      "id": "uuid",
      "class_code": "CS101-A",
      "course_name": "Introduction to Computer Science",
      "section": "A"
    },
    "date": "2025-01-15",
    "attendance_records": [
      {
        "enrollment_id": "uuid",
        "student": {
          "id": "uuid",
          "student_id": "STU001",
          "name": "John Doe"
        },
        "status": "PRESENT",
        "notes": ""
      }
    ],
    "summary": {
      "total_students": 25,
      "present": 23,
      "absent": 1,
      "late": 1,
      "excused": 0
    }
  }
}
```

---

## 📊 Grade Management Endpoints (`/api/v1/grades/`)

### 1. List Grades
- **Method:** `GET`
- **URL:** `/api/v1/grades/`
- **Permissions:** Authenticated (Students see own, Instructors see their classes, Admin see all)
- **Query Parameters:**
  - `enrollment_id` (optional): Filter by enrollment
  - `class_id` (optional): Filter by class
  - `page` (optional): Page number
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "count": 100,
    "results": [
      {
        "id": "uuid",
        "enrollment": "uuid",
        "exam": "uuid",
        "student_name": "John Doe",
        "student_id": "STU001",
        "class_code": "CS101-A",
        "course_name": "Introduction to Computer Science",
        "assignment_name": "Midterm Exam",
        "marks_obtained": 85.00,
        "total_marks": 100.00,
        "percentage": 85.00,
        "weight_percentage": 30.00,
        "weighted_score": 25.50,
        "graded_by_name": "Dr. Smith",
        "graded_date": "2025-01-15T10:00:00Z",
        "comments": "Good work",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z"
      }
    ]
  }
}
```

### 2. Submit Grade
- **Method:** `POST`
- **URL:** `/api/v1/grades/`
- **Permissions:** Admin, Instructor (for own classes)
- **Request Body:**
```json
{
  "enrollment": "enrollment_uuid",
  "exam": "exam_uuid",
  "assignment_name": "Midterm Exam",
  "marks_obtained": 85.00,
  "total_marks": 100.00,
  "weight_percentage": 30.00,
  "comments": "Good work"
}
```
- **Success Response (201):**
```json
{
  "status": "success",
  "message": "Grade submitted successfully",
  "data": { /* Grade object */ }
}
```

### 3. Update Grade
- **Method:** `PUT` / `PATCH`
- **URL:** `/api/v1/grades/{id}/`
- **Permissions:** Admin, Instructor (for own classes)
- **Request Body:**
```json
{
  "marks_obtained": 90.00,
  "comments": "Updated: Excellent work"
}
```
- **Success Response (200):** Updated grade object

### 4. Get Student Grades
- **Method:** `GET`
- **URL:** `/api/v1/grades/student/{student_id}/`
- **Permissions:** Authenticated (own data or Admin/Instructor)
- **Query Parameters:**
  - `class_id` (optional): Filter by class
  - `semester` (optional): FALL, SPRING, SUMMER
  - `academic_year` (optional): Year number
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "student": {
      "id": "uuid",
      "student_id": "STU001",
      "name": "John Doe",
      "gpa": 3.75
    },
    "semester_gpa": 3.80,
    "courses": [
      {
        "class": {
          "class_code": "CS101-A",
          "course_name": "Introduction to Computer Science",
          "credits": 3,
          "instructor_name": "Dr. Smith"
        },
        "grades": [
          {
            "assignment_name": "Midterm Exam",
            "marks_obtained": 85.00,
            "total_marks": 100.00,
            "percentage": 85.00,
            "weight_percentage": 30.00
          }
        ],
        "final_grade": "A",
        "grade_points": 4.00
      }
    ]
  }
}
```

### 5. Finalize Grade
- **Method:** `POST`
- **URL:** `/api/v1/grades/enrollment/{enrollment_id}/finalize/`
- **Permissions:** Admin, Instructor (for own classes)
- **Request Body:**
```json
{
  "final_grade": "A"
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "Final grade submitted successfully",
  "data": {
    "enrollment_id": "uuid",
    "student_name": "John Doe",
    "class_code": "CS101-A",
    "final_grade": "A",
    "grade_points": 4.00,
    "status": "COMPLETED"
  }
}
```

### 6. Get Class Statistics
- **Method:** `GET`
- **URL:** `/api/v1/grades/class/{class_id}/statistics/`
- **Permissions:** Authenticated (Instructor for own classes, Admin/Registrar for all)
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "class": {
      "class_code": "CS101-A",
      "course_name": "Introduction to Computer Science",
      "section": "A",
      "instructor_name": "Dr. Smith"
    },
    "semester": "FALL",
    "academic_year": 2023,
    "statistics": {
      "total_students": 25,
      "average_grade": 3.50,
      "median_grade": 3.60,
      "grade_distribution": {
        "A+": 2,
        "A": 5,
        "B+": 8,
        "B": 6,
        "C+": 3,
        "C": 1,
        "D": 0,
        "F": 0
      }
    },
    "student_grades": [ /* Detailed student grades */ ]
  }
}
```

---

## 🏢 Room Management Endpoints (`/api/v1/rooms/`)

### 1. List Rooms
- **Method:** `GET`
- **URL:** `/api/v1/rooms/`
- **Permissions:** Authenticated
- **Query Parameters:**
  - `capacity_min` (optional): Minimum capacity
  - `room_type` (optional): CLASSROOM, LAB, LECTURE_HALL, SEMINAR
  - `is_available` (optional): true/false
  - `page` (optional): Page number
- **Success Response (200):** Paginated room list

### 2. Create Room
- **Method:** `POST`
- **URL:** `/api/v1/rooms/`
- **Permissions:** Admin
- **Request Body:**
```json
{
  "room_number": "101",
  "building": "Science Building",
  "capacity": 30,
  "room_type": "CLASSROOM",
  "equipment": ["projector", "whiteboard"],
  "is_available": true
}
```
- **Success Response (201):** Room object

### 3. Get Room Details
- **Method:** `GET`
- **URL:** `/api/v1/rooms/{id}/`
- **Permissions:** Authenticated
- **Success Response (200):** Room object

### 4. Update Room
- **Method:** `PUT` / `PATCH`
- **URL:** `/api/v1/rooms/{id}/`
- **Permissions:** Admin
- **Request Body:**
```json
{
  "capacity": 35,
  "equipment": ["projector", "whiteboard", "computers"],
  "is_available": false
}
```
- **Success Response (200):** Updated room object

### 5. Delete Room
- **Method:** `DELETE`
- **URL:** `/api/v1/rooms/{id}/`
- **Permissions:** Admin
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "Room deleted successfully"
}
```
- **Error Response (400):** Cannot delete room with active classes

### 6. Get Available Rooms
- **Method:** `GET`
- **URL:** `/api/v1/rooms/available/`
- **Permissions:** Authenticated
- **Query Parameters:**
  - `capacity_min` (optional): Minimum capacity
  - `room_type` (optional): CLASSROOM, LAB, LECTURE_HALL, SEMINAR
- **Success Response (200):** List of available rooms

---

## 📅 Exam Management Endpoints (`/api/v1/exams/`)

### 1. List Exams
- **Method:** `GET`
- **URL:** `/api/v1/exams/`
- **Permissions:** Authenticated
- **Query Parameters:**
  - `class_id` (optional): Filter by class
  - `exam_type` (optional): MIDTERM, FINAL, QUIZ, PROJECT
  - `start_date` (optional): Start date filter
  - `end_date` (optional): End date filter
  - `student_id` (optional): Filter by student enrollments
  - `page` (optional): Page number
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "count": 20,
    "results": [
      {
        "id": "uuid",
        "class_instance": "uuid",
        "class_code": "CS101-A",
        "course_name": "Introduction to Computer Science",
        "exam_type": "MIDTERM",
        "exam_date": "2025-02-15T10:00:00Z",
        "duration_minutes": 120,
        "room": {
          "id": "uuid",
          "room_number": "101",
          "building": "Science Building",
          "capacity": 30
        },
        "total_marks": 100.00,
        "instructions": "Bring calculator",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
      }
    ]
  }
}
```

### 2. Create Exam
- **Method:** `POST`
- **URL:** `/api/v1/exams/`
- **Permissions:** Admin, Registrar
- **Request Body:**
```json
{
  "class_instance": "class_uuid",
  "exam_type": "MIDTERM",
  "exam_date": "2025-02-15T10:00:00Z",
  "duration_minutes": 120,
  "room": "room_uuid",
  "total_marks": 100.00,
  "instructions": "Bring calculator"
}
```
- **Success Response (201):** Exam object

### 3. Get Exam Details
- **Method:** `GET`
- **URL:** `/api/v1/exams/{id}/`
- **Permissions:** Authenticated
- **Success Response (200):** Exam object

### 4. Update Exam
- **Method:** `PUT` / `PATCH`
- **URL:** `/api/v1/exams/{id}/`
- **Permissions:** Admin, Registrar
- **Request Body:**
```json
{
  "exam_date": "2025-02-16T10:00:00Z",
  "room": "new_room_uuid",
  "instructions": "Updated instructions"
}
```
- **Success Response (200):** Updated exam object

---

## 🔔 Notification Endpoints (`/api/v1/notifications/`)

### 1. List Notifications
- **Method:** `GET`
- **URL:** `/api/v1/notifications/`
- **Permissions:** Authenticated (own notifications)
- **Query Parameters:**
  - `is_read` (optional): true/false
  - `notification_type` (optional): GRADE, ATTENDANCE, ENROLLMENT, ANNOUNCEMENT, SYSTEM
  - `page` (optional): Page number
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "unread_count": 5,
    "results": [
      {
        "id": "uuid",
        "notification_type": "GRADE",
        "title": "New Grade Posted",
        "message": "Your grade for CS101 Midterm has been posted",
        "is_read": false,
        "priority": "MEDIUM",
        "related_object": {
          "type": "Grade",
          "id": "uuid"
        },
        "created_at": "2025-01-15T10:00:00Z"
      }
    ]
  }
}
```

### 2. Mark Notification as Read
- **Method:** `PUT`
- **URL:** `/api/v1/notifications/{id}/mark-read/`
- **Permissions:** Authenticated (own notifications)
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "Notification marked as read",
  "data": {
    "id": "uuid",
    "is_read": true
  }
}
```

### 3. Mark All Notifications as Read
- **Method:** `POST`
- **URL:** `/api/v1/notifications/mark-all-read/`
- **Permissions:** Authenticated
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "All notifications marked as read",
  "data": {
    "updated_count": 5
  }
}
```

### 4. Delete Notification
- **Method:** `DELETE`
- **URL:** `/api/v1/notifications/{id}/`
- **Permissions:** Authenticated (own notifications)
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "Notification deleted successfully"
}
```

---

## 💬 Message Endpoints (`/api/v1/messages/`)

### 1. List Messages
- **Method:** `GET`
- **URL:** `/api/v1/messages/`
- **Permissions:** Authenticated (own messages)
- **Query Parameters:**
  - `folder` (optional): inbox (default) or sent
  - `is_read` (optional): true/false
  - `search` (optional): Search in subject or body
  - `page` (optional): Page number
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "unread_count": 3,
    "results": [
      {
        "id": "uuid",
        "sender": { /* User object */ },
        "sender_name": "Dr. Smith",
        "recipient": { /* User object */ },
        "recipient_name": "John Doe",
        "subject": "Question about Assignment",
        "body": "Please see me after class...",
        "is_read": false,
        "parent_message": null,
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z"
      }
    ]
  }
}
```

### 2. Send Message
- **Method:** `POST`
- **URL:** `/api/v1/messages/`
- **Permissions:** Authenticated
- **Request Body:**
```json
{
  "recipient_id": "recipient_uuid",
  "subject": "Question about Assignment",
  "body": "Please see me after class...",
  "parent_message": null
}
```
- **Success Response (201):**
```json
{
  "status": "success",
  "message": "Message sent successfully",
  "data": { /* Message object */ }
}
```

### 3. Get Message Details
- **Method:** `GET`
- **URL:** `/api/v1/messages/{id}/`
- **Permissions:** Authenticated (sender or recipient)
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "sender": { /* User object */ },
    "recipient": { /* User object */ },
    "subject": "Question about Assignment",
    "body": "Please see me after class...",
    "is_read": true,
    "parent_message": null,
    "replies": [
      {
        "id": "uuid",
        "sender_name": "John Doe",
        "body": "Thank you, I will.",
        "created_at": "2025-01-15T11:00:00Z"
      }
    ],
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z"
  }
}
```

### 4. Delete Message
- **Method:** `DELETE`
- **URL:** `/api/v1/messages/{id}/`
- **Permissions:** Authenticated (sender or recipient)
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "Message deleted successfully"
}
```

---

## 📋 Student Request Endpoints (`/api/v1/student-requests/`)

### 1. List Student Requests
- **Method:** `GET`
- **URL:** `/api/v1/student-requests/`
- **Permissions:** Authenticated (Students see own, Admin/Registrar see all)
- **Query Parameters:**
  - `status` (optional): PENDING, IN_PROGRESS, APPROVED, REJECTED
  - `request_type` (optional): TRANSCRIPT, CERTIFICATE, COURSE_ADD, COURSE_DROP, GRADE_APPEAL, OTHER
  - `page` (optional): Page number
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "count": 10,
    "results": [
      {
        "id": "uuid",
        "student_info": {
          "id": "uuid",
          "student_id": "STU001",
          "name": "John Doe"
        },
        "request_type": "TRANSCRIPT",
        "subject": "Request for Official Transcript",
        "description": "I need an official transcript for job application",
        "status": "PENDING",
        "processed_by_info": null,
        "response": null,
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z"
      }
    ]
  }
}
```

### 2. Submit Request
- **Method:** `POST`
- **URL:** `/api/v1/student-requests/`
- **Permissions:** Student
- **Request Body:**
```json
{
  "request_type": "TRANSCRIPT",
  "subject": "Request for Official Transcript",
  "description": "I need an official transcript for job application"
}
```
- **Success Response (201):**
```json
{
  "status": "success",
  "message": "Request submitted successfully",
  "data": { /* Request object */ }
}
```

### 3. Update Request Status
- **Method:** `PUT` / `PATCH`
- **URL:** `/api/v1/student-requests/{id}/`
- **Permissions:** Admin, Registrar
- **Request Body:**
```json
{
  "status": "APPROVED",
  "response": "Your transcript has been generated and sent to your email."
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "message": "Request updated successfully",
  "data": { /* Updated request object */ }
}
```

---

## 📊 Report Endpoints (`/api/v1/reports/`)

### 1. Generate Transcript
- **Method:** `GET`
- **URL:** `/api/v1/reports/transcript/{student_id}/`
- **Permissions:** Authenticated (own transcript or Admin/Registrar)
- **Query Parameters:**
  - `format` (optional): pdf (default) or json
- **Success Response (200):**
  - PDF: Binary PDF file with Content-Type: application/pdf
  - JSON: Transcript data object

### 2. Generate Attendance Report
- **Method:** `POST`
- **URL:** `/api/v1/reports/attendance/`
- **Permissions:** Authenticated (own data or Admin/Registrar)
- **Request Body:**
```json
{
  "student_id": "student_uuid",
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "format": "pdf"
}
```
- **Success Response (200):**
  - PDF/CSV: Binary file download
  - JSON: Report data object

### 3. Generate Grade Report
- **Method:** `POST`
- **URL:** `/api/v1/reports/grades/`
- **Permissions:** Authenticated (Instructor for own classes, Admin/Registrar for all)
- **Request Body:**
```json
{
  "class_id": "class_uuid",
  "format": "pdf"
}
```
- **Success Response (200):**
  - PDF/CSV: Binary file download
  - JSON: Report data object

---

## 📈 Dashboard Endpoints (`/api/v1/dashboard/`)

### 1. Admin Dashboard
- **Method:** `GET`
- **URL:** `/api/v1/dashboard/admin/`
- **Permissions:** Admin
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "statistics": {
      "total_students": 500,
      "active_students": 480,
      "total_courses": 150,
      "active_classes": 200,
      "total_instructors": 50,
      "average_class_size": 25.5
    },
    "enrollment_trends": [
      {
        "semester": "FALL",
        "academic_year": 2023,
        "enrollment_count": 1200
      }
    ],
    "recent_activities": [ /* Audit log entries */ ],
    "pending_requests": 15,
    "attendance_overview": {
      "average_attendance_rate": 85.5,
      "classes_below_threshold": 5
    }
  }
}
```

### 2. Student Dashboard
- **Method:** `GET`
- **URL:** `/api/v1/dashboard/student/`
- **Permissions:** Student
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "student_profile": {
      "student_id": "STU001",
      "name": "John Doe",
      "academic_status": "Active",
      "cumulative_gpa": 3.75
    },
    "current_semester": {
      "semester": "FALL",
      "academic_year": 2023,
      "enrolled_courses": 5,
      "total_credits": 15,
      "semester_gpa": 3.80
    },
    "enrolled_classes": [ /* Class objects */ ],
    "upcoming_exams": [ /* Exam objects */ ],
    "recent_grades": [ /* Grade objects */ ],
    "attendance_summary": {
      "attendance_rate": 92.5,
      "classes_at_risk": 0
    },
    "unread_notifications": 5,
    "unread_messages": 2
  }
}
```

### 3. Instructor Dashboard
- **Method:** `GET`
- **URL:** `/api/v1/dashboard/instructor/`
- **Permissions:** Instructor
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "instructor_profile": {
      "name": "Dr. Smith",
      "department": "Computer Science"
    },
    "current_semester": {
      "semester": "FALL",
      "academic_year": 2023,
      "total_classes": 3,
      "total_students": 75
    },
    "my_classes": [ /* Class objects with attendance stats */ ],
    "upcoming_exams": [ /* Exam objects */ ],
    "pending_grading": 15,
    "recent_activities": [ /* Audit log entries */ ]
  }
}
```

---

## 🔒 Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "status": "error",
  "message": "Validation error",
  "code": "VALIDATION_ERROR",
  "errors": {
    "field_name": ["Error message"]
  },
  "timestamp": "2025-01-15T10:00:00Z"
}
```

### 401 Unauthorized
```json
{
  "status": "error",
  "message": "Authentication credentials were not provided",
  "code": "AUTHENTICATION_REQUIRED",
  "timestamp": "2025-01-15T10:00:00Z"
}
```

### 403 Forbidden
```json
{
  "status": "error",
  "message": "You do not have permission to perform this action",
  "code": "PERMISSION_DENIED",
  "timestamp": "2025-01-15T10:00:00Z"
}
```

### 404 Not Found
```json
{
  "status": "error",
  "message": "Resource not found",
  "code": "RESOURCE_NOT_FOUND",
  "timestamp": "2025-01-15T10:00:00Z"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "An error occurred processing your request",
  "code": "INTERNAL_ERROR",
  "timestamp": "2025-01-15T10:00:00Z"
}
```

---

## 📝 Notes

1. **Pagination:** Most list endpoints support pagination with `page` and `page_size` query parameters
2. **Filtering:** Use query parameters to filter results (e.g., `?status=ACTIVE&role=STUDENT`)
3. **Search:** Many endpoints support `search` parameter for text search
4. **Ordering:** Use `ordering` parameter (e.g., `?ordering=-created_at` for descending)
5. **File Uploads:** Use `multipart/form-data` for file uploads (profile pictures, documents)
6. **Date Formats:** Use ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)
7. **UUIDs:** All IDs are UUIDs (string format)

