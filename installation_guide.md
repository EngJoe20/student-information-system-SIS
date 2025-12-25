# Student Information System - Installation Guide

## 🚀 Quick Start (Development)

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (optional, SQLite works for dev)
- Git

### Step 1: Clone Repository

```bash
git clone <your-repo-url>
cd student-information-system-Academia
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Environment Configuration

```bash
# Create .env file
cp .env.example .env

# Edit .env with your settings
# For development, minimal config:
SECRET_KEY=your-secret-key-generate-one
DEBUG=True
```

### Step 5: Database Setup

```bash
# Create necessary directories
mkdir -p logs media staticfiles

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 6: Run Development Server

```bash
## server for backend
python manage.py runserver

## server for frontend
python -m http.server 8080
```

### Step 7: Access the Application

- **API Root**: http://localhost:8000/
- **frontend Root**: http://localhost:8080/
- **Admin Panel**: http://localhost:8000/admin/
- **Swagger API Docs**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

---

## 📝 .env Configuration

### Minimal Development Setup

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_SETTINGS_MODULE=sis_backend.settings.development

# Database (SQLite - default for development)
# No configuration needed, will use db.sqlite3

# JWT
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800

# Email (Console backend for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# URLs
SITE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:8080
```

### Full Production Setup

```env
# Django
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DJANGO_SETTINGS_MODULE=sis_backend.settings.production

# Database - PostgreSQL
DB_NAME=sis_db
DB_USER=sis_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800

# Email - Gmail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@your-domain.com

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com

# Security
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True

# URLs
SITE_URL=https://your-domain.com
FRONTEND_URL=https://your-frontend.com
```

---

## 🗄️ PostgreSQL Setup (Optional for Development)

### Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from: https://www.postgresql.org/download/windows/
```

### Create Database

```bash
# Access PostgreSQL
sudo -u postgres psql

# Run these commands:
CREATE DATABASE sis_db;
CREATE USER sis_user WITH PASSWORD 'your_password';
ALTER ROLE sis_user SET client_encoding TO 'utf8';
ALTER ROLE sis_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE sis_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE sis_db TO sis_user;
\q
```

### Update .env for PostgreSQL

```env
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=sis_db
DATABASE_USER=sis_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

---

## 🔑 Initial Data Setup

### Create Superuser (Admin)

```bash
python manage.py createsuperuser
# Enter: username, email, password
```

### Create Sample Data (Optional)

```bash
# Create management command: students/management/commands/create_sample_data.py
python manage.py create_sample_data
```

### Sample Data Script

```python
# students/management/commands/create_sample_data.py
from django.core.management.base import BaseCommand
from accounts.models import User
from students.models import Student
from courses.models import Course, Class, Room
from datetime import date

class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **kwargs):
        # Create users
        admin = User.objects.create_user(
            username='admin',
            email='admin@sis.com',
            password='Admin123!',
            first_name='Admin',
            last_name='User',
            role='ADMIN'
        )

        instructor = User.objects.create_user(
            username='instructor1',
            email='instructor@sis.com',
            password='Instructor123!',
            first_name='John',
            last_name='Smith',
            role='INSTRUCTOR'
        )

        # Create student
        student_user = User.objects.create_user(
            username='student1',
            email='student@sis.com',
            password='Student123!',
            first_name='Jane',
            last_name='Doe',
            role='STUDENT'
        )

        student = Student.objects.create(
            user=student_user,
            student_id='S2025001',
            date_of_birth=date(2005, 1, 1),
            gender='FEMALE',
            enrollment_date=date.today(),
            academic_status='ACTIVE'
        )

        # Create course
        course = Course.objects.create(
            course_code='CS101',
            course_name='Introduction to Computer Science',
            description='Fundamentals of programming',
            credits=3,
            department='Computer Science'
        )

        # Create room
        room = Room.objects.create(
            room_number='101',
            building='Main Building',
            capacity=30,
            room_type='CLASSROOM'
        )

        # Create class
        class_obj = Class.objects.create(
            course=course,
            instructor=instructor,
            class_code='CS101-001',
            section='001',
            semester='FALL',
            academic_year=2025,
            max_capacity=30,
            room=room,
            status='OPEN'
        )

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
```

---

## 🧪 Testing the Installation

### Test API Endpoints

```bash
# Test login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}'

# Test with Swagger
# Visit: http://localhost:8000/swagger/
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
# or
start htmlcov/index.html  # Windows
```

---

## 📚 Useful Management Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server for backend
python manage.py runserver

# Run development server for frontend
python -m http.server 8080

# Run on custom port
python manage.py runserver 0.0.0.0:8080

# Django shell
python manage.py shell

# Database shell
python manage.py dbshell

# Check for issues
python manage.py check

# Show migrations
python manage.py showmigrations
```

---

## 🔧 Troubleshooting

### Issue: ModuleNotFoundError

```bash
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Database errors

```bash
# Delete database and migrations (DEVELOPMENT ONLY!)
rm db.sqlite3
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate database
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Issue: Port already in use

```bash
# Kill process on port 8000
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: Static files not loading

```bash
python manage.py collectstatic --clear --noinput
```

### Issue: CSRF token errors

```bash
# Clear browser cookies
# Make sure CSRF_COOKIE_HTTPONLY = False in settings
# Check CORS configuration
```

---

## 📊 Database Migrations

### Create New App

```bash
python manage.py startapp app_name
```

### Add to INSTALLED_APPS

```python
# settings/base.py
INSTALLED_APPS = [
    # ...
    'app_name.apps.AppNameConfig',
]
```

### Create Migrations

```bash
python manage.py makemigrations app_name
python manage.py migrate app_name
```

---

## 🔐 Security Checklist

### Development

- [ ] DEBUG=True
- [ ] Use SQLite
- [ ] Console email backend
- [ ] Allow all CORS origins
- [ ] No HTTPS required

### Production

- [ ] DEBUG=False
- [ ] Use PostgreSQL
- [ ] SMTP email backend
- [ ] Specific CORS origins
- [ ] HTTPS enforced
- [ ] Strong SECRET_KEY
- [ ] Configure firewall
- [ ] Set up SSL certificate
- [ ] Configure backups
- [ ] Set up monitoring

---

## 📖 Next Steps

1. **Read Documentation**

   - Review PROJECT_SUMMARY.md
   - Check API documentation at /swagger/
   - Read DEPLOYMENT.md for production

2. **Explore the API**

   - Use Swagger UI for testing
   - Try different user roles
   - Test CRUD operations

3. **Customize**

   - Add your branding
   - Configure email templates
   - Set up your domain

4. **Deploy**
   - Follow DEPLOYMENT.md
   - Set up production database
   - Configure web server
   - Set up SSL

---

## 🆘 Getting Help

### Resources

- **API Docs**: http://localhost:8000/swagger/
- **Project Summary**: PROJECT_SUMMARY.md
- **Deployment Guide**: DEPLOYMENT.md
- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/

### Common Issues

- Check logs in `logs/` directory
- Review error messages carefully
- Verify environment variables
- Check database connectivity
- Ensure all dependencies installed

---

## ✅ Installation Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Database setup complete
- [ ] Migrations applied
- [ ] Superuser created
- [ ] Development server running
- [ ] Can access admin panel
- [ ] Can access Swagger docs
- [ ] API endpoints working

---

**Congratulations!** 🎉 Your Student Information System is now installed and ready to use!

For production deployment, see **DEPLOYMENT.md**.
For feature overview, see **PROJECT_SUMMARY.md**.
