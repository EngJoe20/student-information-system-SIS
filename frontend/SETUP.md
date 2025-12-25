# Academia Frontend - Setup Guide

## Overview

This frontend is a complete HTML/CSS/JavaScript implementation using Bootstrap 5, jQuery, and AJAX to connect to the Django REST API backend.

## File Structure

```
frontend/
├── index.html                    # Redirects to login
├── assets/
│   ├── css/
│   │   ├── main.css            # Global styles
│   │   └── auth.css            # Authentication styles
│   └── js/
│       ├── config.js           # Configuration and constants
│       ├── utils.js            # Utility functions
│       ├── auth.js             # Authentication logic
│       └── api.js              # API wrapper functions
├── components/
│   ├── navbar.html             # Reusable navbar
│   └── sidebar.html            # Reusable sidebar
├── pages/
│   ├── auth/
│   │   └── login.html          # Login page with 2FA support
│   ├── dashboard/
│   │   ├── admin.html          # Admin dashboard
│   │   ├── student.html        # Student dashboard
│   │   ├── instructor.html     # Instructor dashboard (to be created)
│   │   └── registrar.html      # Registrar dashboard (to be created)
│   ├── students/
│   │   ├── list.html           # Students list page
│   │   ├── create.html         # Create student (to be created)
│   │   ├── view.html           # View student (to be created)
│   │   └── edit.html           # Edit student (to be created)
│   └── [other modules]/        # Similar structure for other modules
└── README.md                    # Architecture documentation
```

## Setup Instructions

### 1. Configure API Base URL

Edit `frontend/assets/js/config.js` and update the `API_BASE_URL`:

```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000/api/v1',  // Update this
    // ... other config
};
```

### 2. Serve Frontend Files

#### Option A: Using Django Static Files

1. Copy the `frontend` folder to your Django project's `static` directory
2. Configure Django to serve static files
3. Access via: `http://localhost:8000/static/frontend/pages/auth/login.html`

#### Option B: Using Simple HTTP Server

```bash
cd frontend
python -m http.server 8080
# Access via: http://localhost:8080/pages/auth/login.html
```

#### Option C: Using Nginx/Apache

Configure your web server to serve the `frontend` directory as static files.

### 3. CORS Configuration

Ensure your Django backend allows requests from your frontend origin:

```python
# In settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",  # Your frontend URL
    "http://127.0.0.1:8080",
]
```

## Usage

### Authentication Flow

1. User visits login page
2. Enters username/password
3. If 2FA enabled, user enters OTP code
4. JWT tokens stored in localStorage
5. User redirected to role-specific dashboard

### Role-Based Access

- **Student**: Can view own data, enroll in classes
- **Instructor**: Can manage assigned classes, record attendance, submit grades
- **Admin**: Full access to all modules
- **Registrar**: Student management, enrollment, reports

### API Integration

All API calls use the wrapper functions in `api.js`:

```javascript
// Example: Get students list
StudentAPI.list({ search: 'john', page: 1 })
    .then(function(response) {
        if (response.status === 'success') {
            // Handle data
            console.log(response.data.results);
        }
    })
    .catch(function(error) {
        // Handle error
        showToast('Failed to load students', 'error');
    });
```

## Key Features Implemented

✅ **Authentication**
- Login with username/password
- 2FA support (TOTP)
- JWT token management
- Auto token refresh
- Logout functionality

✅ **Dashboards**
- Student dashboard with stats, classes, exams, grades
- Admin dashboard with system-wide statistics
- Role-based navigation

✅ **Student Management**
- List students with search and filters
- Pagination support
- Role-based create/edit buttons

✅ **UI Components**
- Responsive Bootstrap 5 layout
- Reusable navbar and sidebar
- Toast notifications
- Loading indicators
- Error handling

## Pages to Complete

Based on the pattern established, create similar pages for:

1. **Students Module**
   - ✅ `list.html` (done)
   - ⏳ `create.html`
   - ⏳ `view.html`
   - ⏳ `edit.html`

2. **Courses Module**
   - ⏳ `list.html`
   - ⏳ `create.html`
   - ⏳ `view.html`
   - ⏳ `edit.html`

3. **Classes Module**
   - ⏳ `list.html`
   - ⏳ `create.html`
   - ⏳ `view.html`
   - ⏳ `timetable.html`

4. **Enrollments Module**
   - ⏳ `list.html`
   - ⏳ `create.html`

5. **Attendance Module**
   - ⏳ `list.html`
   - ⏳ `record.html`
   - ⏳ `bulk-record.html`

6. **Grades Module**
   - ⏳ `list.html`
   - ⏳ `submit.html`
   - ⏳ `statistics.html`

7. **Other Modules**
   - Notifications, Messages, Requests, etc.

## Pattern for Creating New Pages

1. **Copy template structure** from `students/list.html`
2. **Load navbar and sidebar** components
3. **Check authentication/role** permissions
4. **Call appropriate API** from `api.js`
5. **Render data** using utility functions
6. **Handle errors** with toast notifications

## Testing

1. Start Django backend: `python manage.py runserver`
2. Serve frontend files: `python -m http.server 8080`
3. Login with test credentials
4. Test each role's dashboard and permissions

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Notes

- All API endpoints are documented in `api_endpoints.md`
- JWT tokens are stored in localStorage (consider httpOnly cookies for production)
- Error handling includes automatic token refresh on 401 errors
- Role-based UI visibility is handled client-side (backend validates permissions)

## Production Considerations

1. **Security**
   - Use HTTPS
   - Consider httpOnly cookies for tokens
   - Implement CSRF protection
   - Sanitize all user inputs

2. **Performance**
   - Minify CSS/JS files
   - Enable gzip compression
   - Use CDN for Bootstrap/jQuery
   - Implement caching strategies

3. **Monitoring**
   - Add error tracking (Sentry)
   - Log API calls
   - Monitor performance

4. **Deployment**
   - Build process for minification
   - Environment-specific configs
   - CI/CD pipeline

