# student-information-system-SIS

## Complete Folder Structure
```
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
├── .env                          # Environment variables (not in git)
├── .gitignore
├── manage.py
├── requirements.txt
├── pytest.ini                    # Pytest configuration
├── README.md
└── LICENSE
```