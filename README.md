# Student Information System (SIS)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

A comprehensive Student Information System built with Django REST Framework, featuring complete academic management, role-based access control, real-time notifications, and advanced reporting capabilities.

## 🎯 Features

### Core Features
- ✅ **Authentication & Authorization**
  - JWT token-based authentication
  - Two-Factor Authentication (2FA)
  - Role-Based Access Control (4 roles)
  - Password reset & recovery
  
- ✅ **Student Management**
  - Complete student profiles
  - Academic status tracking
  - GPA calculation (4.0 scale)
  - Enrollment history
  
- ✅ **Course Management**
  - Course catalog with prerequisites
  - Class scheduling & room assignment
  - Instructor management
  - Timetable generation
  
- ✅ **Attendance System**
  - Daily attendance tracking
  - Bulk attendance recording
  - Attendance alerts (<75%)
  - Comprehensive reports
  
- ✅ **Grade Management**
  - Assignment & exam grades
  - Weighted average calculation
  - Final grade submission
  - Automatic GPA updates
  
- ✅ **Communication**
  - In-app notifications
  - Email notifications
  - Internal messaging system
  - Student service requests
  
- ✅ **Reporting**
  - PDF transcripts
  - Attendance reports
  - Grade reports
  - CSV/Excel exports
  
- ✅ **Advanced Features**
  - Global search
  - Role-specific dashboards
  - File upload management
  - Bulk import/export
  - Audit logging

## 🏗️ Technology Stack

**Backend:**
- Python 3.11+
- Django 5.0
- Django REST Framework 3.14
- PostgreSQL 15+ / SQLite (dev)
- Redis 7+ (caching)

**Key Libraries:**
- PyJWT (JWT authentication)
- PyOTP (2FA)
- ReportLab (PDF generation)
- OpenPyXL (Excel processing)
- drf-yasg (API documentation)

## 📁 Project Structure

```text
student-information-system-SIS/
│
├── venv/                          # Virtual environment (not in git)
│
├── sis_backend/                   # Main project directory
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── settings/                  # Split settings
│   │   ├── __init__.py
│   │   ├── base.py               # Base settings
│   │   ├── development.py        # Dev settings
│   │   └── production.py         # Prod settings
│   └── urls.py                   # Main URL configuration
│
├── accounts/                      # User & Authentication app
│   ├── migrations/
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                 # User model
│   ├── serializers.py            # User serializers
│   ├── views.py                  # Auth & User views
│   ├── urls.py                   # Auth routes
│   ├── permissions.py            # Custom permissions
│   ├── authentication.py         # Custom auth classes
│   ├── managers.py               # Custom user manager
│   └── tests.py
│
├── students/                      # Student management app
│   ├── migrations/
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                 # Student, Enrollment models
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── dashboard/                      # Dashboard views for Admin, Student, and Instructor roles.
│   ├── migrations/
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                 
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── courses/                       # Course & Class management
│   ├── migrations/
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                 # Course, Class, Room, Exam models
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── attendance/                    # Attendance management
│   ├── migrations/
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                 # Attendance model
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── grades/                        # Grade management
│   ├── migrations/
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                 # Grade model
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── notifications/                 # Notifications & Messages
│   ├── migrations/
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                 # Notification, Message, StudentRequest
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── core/                          # Core utilities & shared code
│   ├── migrations/
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                 # AuditLog model
│   ├── middleware.py             # Custom middleware
│   ├── utils.py                  # Helper functions
│   ├── exceptions.py             # Custom exceptions
│   ├── pagination.py             # Custom pagination
│   └── tests.py
│
├── media/                         # Uploaded files
│   ├── profile_pictures/
│   ├── documents/
│   └── transcripts/
│
├── static/                        # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/                     # Email templates
│   └── emails/
│       ├── password_reset.html
│       ├── grade_notification.html
│       └── welcome.html
│
├── logs/                          # Application logs
│   ├── django.log
│   ├── api.log
│   └── security.log
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_authentication.py
│   ├── test_students.py
│   ├── test_courses.py
│   └── fixtures/
│       └── test_data.json
│
├── scripts/                       # Utility scripts
│   ├── seed_database.py
│   ├── generate_test_data.py
│   └── backup_database.sh
│
├── .env.example                   # Environment variables template
├── .env                           # Environment variables (not in git)
├── .gitignore
├── manage.py
├── requirements.txt
├── pytest.ini                     # Pytest configuration
├── README.md
└── LICENSE
```

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.11 or higher
python --version

# PostgreSQL (optional, SQLite works for dev)
psql --version

# Git
git --version
```

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd student-information-system-SIS
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Environment configuration**
```bash
# Create .env file
cp .env.example .env

# Edit .env with your settings
# For development, minimal config needed:
SECRET_KEY=your-secret-key-here
DEBUG=True
```

5. **Database setup**
```bash
# Create directories
mkdir -p logs media staticfiles

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed database with test data
python scripts/seed_database.py
```

6. **Run development server**
```bash
python manage.py runserver
```

7. **Access the application**
- API Root: http://localhost:8000/
- Admin Panel: http://localhost:8000/admin/
- API Documentation: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## 🔐 Test Accounts

After running `seed_database.py`:

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| Admin | admin | Admin123! | Full system access |
| Registrar | registrar1 | Registrar123! | Student & course management |
| Instructor | instructor1 | Instructor123! | Grade & attendance |
| Student | student1 | Student123! | View own information |

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

### API Endpoint Summary
- **Authentication**: 6 endpoints
- **Users**: 7 endpoints
- **Students**: 8 endpoints
- **Courses & Classes**: 12 endpoints
- **Enrollment**: 3 endpoints
- **Attendance**: 4 endpoints
- **Grades**: 5 endpoints
- **Exams**: 3 endpoints
- **Rooms**: 5 endpoints
- **Notifications**: 4 endpoints
- **Messages**: 4 endpoints
- **Reports**: 3 endpoints
- **Dashboards**: 3 endpoints
- **Advanced**: 10+ endpoints

**Total: 80+ API Endpoints**

## 🔧 Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL - optional)
DB_NAME=sis_db
DB_USER=sis_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800

# Email (for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# URLs
SITE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

See `INSTALLATION.md` for complete configuration guide.

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_authentication.py -v

# Run with coverage
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 📊 Scripts

### Database Seeding
```bash
# Seed initial data (20 students, courses, etc.)
python scripts/seed_database.py

# Generate comprehensive test data
python scripts/generate_test_data.py
```

### Database Backup
```bash
# Linux/Mac
./scripts/backup_database.sh

# Windows
scripts\backup_database.bat
```

See `scripts/README.md` for detailed usage.

## 🚢 Deployment

### Development
```bash
python manage.py runserver
```

### Production
See `DEPLOYMENT.md` for complete production deployment guide including:
- PostgreSQL setup
- Gunicorn configuration
- Nginx setup
- SSL certificates
- Security hardening
- Monitoring & logging

Quick production start:
```bash
gunicorn sis_backend.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120
```

## 📖 Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Quick setup guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete overview
- **[scripts/README.md](scripts/README.md)** - Utility scripts guide
- **API Docs** - Available at `/swagger/` endpoint

## 🔒 Security Features

- JWT authentication with token rotation
- Two-factor authentication (TOTP)
- Password hashing with bcrypt
- Role-based access control
- CSRF protection
- Rate limiting
- Audit logging
- SQL injection prevention
- XSS protection
- HTTPS enforcement (production)

## 📈 Performance

- Database query optimization
- Redis caching for sessions
- Static file compression
- Connection pooling
- Pagination for large datasets
- Efficient indexing

## 🎓 User Roles & Permissions

### Student
- View own profile & grades
- Enroll in courses
- Check attendance
- Submit service requests
- Internal messaging

### Instructor  
- Manage assigned classes
- Record attendance
- Submit grades
- View class rosters
- Schedule exams

### Registrar
- Manage students
- Create courses & classes
- Process enrollments
- Handle student requests
- Generate reports

### Admin
- Full system access
- User management
- System configuration
- Audit logs
- All reports

## 🛠️ Development

### Project Setup for Development
```bash
# Install development dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load test data
python scripts/seed_database.py

# Run server
python manage.py runserver
```

### Code Style
```bash
# Format code
black .

# Lint code
flake8 .

# Run tests
pytest
```

## 📊 Database Models

13 Core Models:
1. User (Custom user with RBAC)
2. Student
3. Course
4. Class
5. Room
6. Enrollment
7. Attendance
8. Grade
9. Exam
10. Notification
11. Message
12. StudentRequest
13. AuditLog

See `PROJECT_SUMMARY.md` for complete model documentation.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Django & Django REST Framework communities
- ReportLab for PDF generation
- All contributors and testers

## 📞 Support

- **Documentation**: See docs in project root
- **Issues**: [GitHub Issues](https://github.com/yourorg/sis-backend/issues)
- **Email**: support@yourcompany.com

## 🗺️ Roadmap

### Phase 2 (Future)
- [ ] Learning Management System integration
- [ ] Financial management
- [ ] Library management
- [ ] Parent portal
- [ ] Mobile app

### Phase 3 (Advanced)
- [ ] AI-powered analytics
- [ ] Predictive models
- [ ] Alumni management
- [ ] Advanced scheduling

## 📸 Screenshots

(Add screenshots of key features)

## 🎯 Project Status

**Status**: ✅ Production Ready

- All core features implemented
- Comprehensive testing
- Production deployment guide
- Complete documentation
- Security hardening
- Performance optimized

## 🔄 Version History

- **v1.0.0** (2024-12) - Initial release
  - Complete SIS implementation
  - 80+ API endpoints
  - Full documentation

---

**Built with ❤️ using Django**