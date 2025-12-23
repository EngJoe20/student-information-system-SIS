# Academia - Project Summary

## Project Overview

**Academia** (formerly Student Information System) is a comprehensive Django REST Framework (DRF) based backend application designed to manage all aspects of academic administration. The system provides a robust API for managing students, courses, enrollments, attendance, grades, notifications, and administrative functions.

**Technology Stack:**
- **Backend Framework:** Django 5.0
- **API Framework:** Django REST Framework 3.14.0
- **Authentication:** JWT (JSON Web Tokens) via `djangorestframework-simplejwt`
- **Database:** SQLite (development), PostgreSQL (production-ready)
- **API Documentation:** Swagger/OpenAPI via `drf-yasg`
- **Additional Features:** 2FA (TOTP), CORS support, audit logging, email notifications

## System Goals

1. **Centralized Academic Management:** Provide a single source of truth for all student, course, and academic data
2. **Role-Based Access Control:** Implement granular permissions for different user types (Admin, Student, Instructor, Registrar)
3. **Automated Workflows:** Streamline enrollment, grading, attendance tracking, and reporting processes
4. **Data Integrity:** Ensure data consistency through validation, constraints, and audit logging
5. **Security & Compliance:** Implement secure authentication, authorization, and comprehensive audit trails
6. **Scalability:** Design for growth with modular architecture and efficient database queries

## User Roles and Responsibilities

### 1. Administrator (ADMIN)
- **Primary Responsibilities:**
  - Full system access and configuration
  - User account management (create, update, delete, role assignment)
  - Course and class management
  - System-wide reports and analytics
  - Room and resource management
  - Exam scheduling
  - Access to all student and instructor data

### 2. Registrar (REGISTRAR)
- **Primary Responsibilities:**
  - Student profile management (create, update student records)
  - Enrollment management (approve, modify enrollments)
  - Class scheduling and capacity management
  - Transcript generation and verification
  - Student request processing (transcripts, certificates, appeals)
  - Academic status management

### 3. Instructor (INSTRUCTOR)
- **Primary Responsibilities:**
  - View assigned classes and student rosters
  - Record and manage attendance for their classes
  - Submit and update grades for assessments
  - Finalize course grades
  - View class statistics and grade distributions
  - Access to class-specific reports
  - Manage exam schedules for their classes

### 4. Student (STUDENT)
- **Primary Responsibilities:**
  - View personal academic profile and transcript
  - Enroll in and drop classes (with validation)
  - View attendance records and grades
  - Access course schedules and exam dates
  - Submit requests (transcripts, certificates, appeals)
  - Receive notifications and messages
  - View dashboard with academic summary

## High-Level Architecture

### Architecture Pattern
The system follows a **RESTful API architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Application                      │
│              (React/Next.js/Vue/Angular)                     │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/HTTPS
                        │ JWT Authentication
┌───────────────────────▼─────────────────────────────────────┐
│              Django REST Framework API Layer               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Accounts │  │ Students │  │ Courses  │  │ Grades   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │Attendance│  │Notifications│ │Dashboard │  │  Core   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│              Django ORM & Business Logic Layer              │
│  • Permission Classes  • Serializers  • ViewSets            │
│  • Business Rules      • Validations  • Utilities           │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    Database Layer                           │
│              (SQLite/PostgreSQL)                            │
│  • Users        • Students    • Courses    • Enrollments    │
│  • Attendance   • Grades      • Exams      • Notifications   │
│  • Audit Logs   • Messages    • Requests                    │
└─────────────────────────────────────────────────────────────┘
```

### Core Modules

1. **accounts** - User authentication, authorization, and user management
2. **students** - Student profiles and enrollment management
3. **courses** - Course catalog, class instances, rooms, and exam scheduling
4. **attendance** - Daily attendance tracking and reporting
5. **grades** - Assessment grading, final grade calculation, and GPA management
6. **notifications** - System notifications, internal messaging, and student requests
7. **dashboard** - Role-specific dashboard statistics and summaries
8. **core** - Shared utilities, exceptions, pagination, audit logging, and report generation

### Data Flow Overview

1. **Authentication Flow:**
   - User submits credentials → JWT tokens generated → Access token used for subsequent requests
   - Optional 2FA: If enabled, temporary token issued → OTP verification → JWT tokens provided

2. **Enrollment Flow:**
   - Student requests enrollment → System validates prerequisites, capacity, schedule conflicts
   - Enrollment created → Class capacity incremented → Notification sent

3. **Grading Flow:**
   - Instructor submits assessment grades → System calculates weighted scores
   - Final grade finalized → Enrollment status updated → Student GPA recalculated → Notification sent

4. **Attendance Flow:**
   - Instructor records attendance (single or bulk) → Records stored with timestamps
   - Attendance statistics calculated → Alerts generated for low attendance

5. **Request Processing Flow:**
   - Student submits request → Status set to PENDING → Admin/Registrar processes
   - Status updated → Response provided → Notification sent to student

## Key System Features

### 1. Authentication & Security
- JWT-based authentication with refresh token rotation
- Two-factor authentication (2FA) using TOTP
- Password reset via email tokens
- Role-based access control (RBAC)
- Comprehensive audit logging
- IP address and user agent tracking

### 2. Student Management
- Student profile creation with user account linkage
- Academic status tracking (Active, Suspended, Graduated, Withdrawn)
- Automatic GPA calculation
- Profile picture upload
- Emergency contact information

### 3. Course & Class Management
- Course catalog with prerequisites
- Class instances per semester with capacity management
- Room assignment and scheduling
- Schedule conflict detection
- Exam scheduling with room allocation

### 4. Enrollment System
- Prerequisite validation
- Capacity checking
- Schedule conflict detection
- Enrollment status tracking (Enrolled, Dropped, Completed, Failed)
- Automatic class capacity updates

### 5. Attendance Tracking
- Daily attendance recording (Present, Absent, Late, Excused)
- Bulk attendance recording
- Attendance statistics and percentage calculation
- Low attendance alerts

### 6. Grading System
- Multiple assessment types with weighted grading
- Automatic grade point calculation
- Final grade finalization
- GPA calculation (semester and cumulative)
- Grade distribution statistics
- Grade appeal requests

### 7. Notifications & Messaging
- System notifications (grades, attendance, enrollment, announcements)
- Internal messaging system
- Student request management
- Email notifications for critical events

### 8. Reporting & Analytics
- Student transcripts (PDF/JSON)
- Attendance reports (PDF/CSV/JSON)
- Grade reports (PDF/CSV/JSON)
- Dashboard statistics per role
- Enrollment trends
- Academic performance analytics

### 9. Audit & Compliance
- Comprehensive audit logging for all actions
- User activity tracking
- Data change history
- Security event logging

## Data Flow Overview

### Request Processing Flow
```
Client Request
    ↓
Middleware (CORS, Security, Audit Logging)
    ↓
URL Router → ViewSet/View
    ↓
Permission Check (Role-based)
    ↓
Serializer Validation
    ↓
Business Logic Processing
    ↓
Database Operations (ORM)
    ↓
Response Serialization
    ↓
Standard Response Format
    ↓
Client Response
```

### Authentication Flow
```
Login Request
    ↓
Credential Validation
    ↓
2FA Check
    ├─→ No 2FA: Generate JWT Tokens
    └─→ 2FA Enabled: Issue Temp Token
            ↓
        OTP Verification
            ↓
        Generate JWT Tokens
    ↓
Return Tokens + User Data
```

### Enrollment Flow
```
Enrollment Request
    ↓
Validate Prerequisites
    ↓
Check Class Capacity
    ↓
Check Schedule Conflicts
    ↓
Create Enrollment
    ↓
Increment Class Enrollment Count
    ↓
Send Notification
    ↓
Return Enrollment Data
```

## Security Considerations

### Authentication Security
- **JWT Tokens:** Short-lived access tokens (1 hour default), long-lived refresh tokens (7 days)
- **Token Blacklisting:** Refresh tokens blacklisted after use/rotation
- **2FA:** Optional TOTP-based two-factor authentication
- **Password Security:** Django's password validators (min length, complexity requirements)

### Authorization Security
- **Role-Based Access Control:** Granular permissions per role
- **Object-Level Permissions:** Users can only access their own data (students see only their records)
- **Permission Classes:** Custom permission classes for each operation type

### Data Security
- **Input Validation:** Comprehensive serializer validation
- **SQL Injection Protection:** Django ORM prevents SQL injection
- **XSS Protection:** Django's built-in XSS protection
- **CSRF Protection:** CSRF middleware enabled
- **Audit Logging:** All critical actions logged with user, IP, and timestamp

### API Security
- **CORS Configuration:** Restricted to allowed origins
- **Rate Limiting:** Can be configured via middleware
- **HTTPS:** Enforced in production (SECURE_SSL_REDIRECT)
- **Secure Cookies:** HTTPOnly and SameSite attributes configured

### Data Privacy
- **Personal Information:** Encrypted at rest (database-level)
- **PII Handling:** Minimal data exposure in API responses
- **Access Logging:** All data access logged for compliance

## Technology Stack Details

### Backend
- **Django 5.0:** Web framework
- **Django REST Framework 3.14.0:** API framework
- **djangorestframework-simplejwt 5.3.1:** JWT authentication
- **drf-yasg 1.21.7:** API documentation
- **django-cors-headers 4.3.1:** CORS handling
- **django-filter 23.5:** Advanced filtering
- **pyotp 2.9.0:** 2FA implementation
- **qrcode 7.4.2:** QR code generation for 2FA

### Database
- **SQLite:** Development database
- **PostgreSQL:** Production-ready (psycopg2-binary)

### Utilities
- **Pillow 10.1.0:** Image processing
- **reportlab 4.4.7:** PDF generation
- **openpyxl 3.1.5:** Excel file handling
- **Faker 22.0.0:** Test data generation

### Development Tools
- **pytest 7.4.3:** Testing framework
- **coverage 7.13.0:** Code coverage
- **black 23.12.1:** Code formatting
- **flake8 7.0.0:** Linting

## Deployment Architecture

### Development
- Django development server
- SQLite database
- Console email backend
- Debug mode enabled

### Production (Recommended)
- **WSGI Server:** Gunicorn or uWSGI
- **Web Server:** Nginx (reverse proxy)
- **Database:** PostgreSQL
- **Static Files:** WhiteNoise or CDN
- **Media Files:** Cloud storage (AWS S3, etc.)
- **Email:** SMTP server (SendGrid, AWS SES, etc.)
- **Monitoring:** Logging, error tracking (Sentry)

## API Standards

### Response Format
All API responses follow a standardized format:
```json
{
  "status": "success|error|2fa_required",
  "message": "Optional message",
  "data": { /* Response data */ },
  "code": "Error code (if error)",
  "errors": { /* Validation errors (if any) */ },
  "timestamp": "ISO 8601 timestamp"
}
```

### Pagination
- Default page size: 20 items
- Page number parameter: `?page=1`
- Response includes: `count`, `next`, `previous`, `results`

### Filtering & Search
- Query parameter filtering: `?field=value`
- Search: `?search=keyword`
- Ordering: `?ordering=field` or `?ordering=-field`

### Error Handling
- HTTP status codes: 200, 201, 400, 401, 403, 404, 500
- Standardized error response format
- Validation errors in `errors` field
- Custom exception handler for consistent error responses

## Future Enhancement Opportunities

1. **Real-time Features:** WebSocket support for live notifications
2. **Mobile App:** Native mobile applications
3. **Advanced Analytics:** Machine learning for predictive analytics
4. **Integration:** LMS integration, payment gateway, library system
5. **Multi-tenancy:** Support for multiple institutions
6. **Advanced Reporting:** Custom report builder
7. **Workflow Engine:** Automated approval workflows
8. **Document Management:** Centralized document storage and versioning
