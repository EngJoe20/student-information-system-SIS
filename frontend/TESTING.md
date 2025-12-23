# Academia Frontend - Testing Guide

## Prerequisites

1. **Django Backend Running**

   - Backend should be running on `http://localhost:8000`
   - Database should be migrated and seeded with test data
   - CORS should be configured to allow frontend origin

2. **Test Users Created**
   - At least one user for each role (Student, Admin, Instructor, Registrar)
   - Users should have valid credentials

## Quick Start Testing

### Step 1: Start Django Backend

```bash
# Navigate to project root
cd E:\student-information-system-Academia

# Activate virtual environment (if using one)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser (if not exists)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Backend should be running at: `http://localhost:8000`

### Step 2: Serve Frontend Files

#### Option A: Python HTTP Server (Recommended for Testing)

```bash
# Navigate to frontend directory
cd frontend

# Start simple HTTP server
# Python 3:
python -m http.server 8080

# Or Python 2:
python -m SimpleHTTPServer 8080
```

Frontend will be available at: `http://localhost:8080`

#### Option B: Using Django Static Files

1. Copy `frontend` folder to Django's `static` directory
2. Configure `STATIC_URL` in settings
3. Access via: `http://localhost:8000/static/frontend/pages/auth/login.html`

#### Option C: Using Live Server (VS Code Extension)

1. Install "Live Server" extension in VS Code
2. Right-click on `frontend/index.html`
3. Select "Open with Live Server"

### Step 3: Configure CORS (If Not Already Done)

Edit `sis_backend/settings/base.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",  # Frontend URL
    "http://127.0.0.1:8080",
    "http://localhost:8080",  # Alternative port
]
```

### Step 4: Update API Base URL (If Needed)

If your backend is not on `localhost:8000`, edit `frontend/assets/js/config.js`:

```javascript
const CONFIG = {
  API_BASE_URL: "http://your-backend-url:8000/api/v1",
  // ...
};
```

## Testing Scenarios

### 1. Authentication Testing

#### Test Login Flow

1. **Open Browser**: Navigate to `http://localhost:8080/pages/auth/login.html`
2. **Test Invalid Credentials**:
   - Enter wrong username/password
   - Should show error toast: "Login failed. Please check your credentials."
3. **Test Valid Login**:
   - Enter correct credentials
   - Should redirect to role-specific dashboard
4. **Test 2FA (If Enabled)**:
   - Login with 2FA-enabled user
   - Should show 2FA form
   - Enter OTP code from authenticator app
   - Should complete login

#### Test Token Storage

1. Open Browser DevTools (F12)
2. Go to Application/Storage tab
3. Check Local Storage
4. Verify these keys exist:
   - `sis_access_token`
   - `sis_refresh_token`
   - `sis_user`

#### Test Auto-Redirect

1. If already logged in, visiting login page should redirect to dashboard
2. If not logged in, visiting protected pages should redirect to login

### 2. Role-Based Testing

#### Test Student Role

1. **Login as Student**
2. **Verify Dashboard**:
   - Should see student dashboard
   - Should show: enrolled courses, GPA, attendance, upcoming exams
3. **Verify Sidebar**:
   - Should show: My Profile, My Enrollments, Available Classes, etc.
   - Should NOT show: Students list, Users management
4. **Test Permissions**:
   - Try accessing `/pages/students/list.html` - Should work (but see only own data)
   - Try accessing `/pages/users/list.html` - Should redirect or show error

#### Test Admin Role

1. **Login as Admin**
2. **Verify Dashboard**:
   - Should see admin dashboard
   - Should show: total students, courses, classes, pending requests
3. **Verify Sidebar**:
   - Should show: Students, Courses, Classes, Users, etc.
4. **Test Permissions**:
   - Should access all pages
   - Should see "Add Student", "Create Course" buttons

#### Test Instructor Role

1. **Login as Instructor**
2. **Verify Dashboard**:
   - Should see instructor dashboard
   - Should show: My Classes, Pending Grading, Upcoming Exams
3. **Verify Sidebar**:
   - Should show: My Classes, Attendance, Grades, Exams
   - Should NOT show: Students management, Users

### 3. API Integration Testing

#### Test Students List Page

1. Navigate to `/pages/students/list.html`
2. **Test Search**:
   - Enter search term in search box
   - Click "Search" button
   - Should filter results
3. **Test Filters**:
   - Select status filter (e.g., "Active")
   - Should filter by status
4. **Test Pagination**:
   - Click "Next" or page numbers
   - Should load different page
5. **Test Sorting**:
   - Change "Order By" dropdown
   - Should re-sort results

#### Test API Error Handling

1. **Test 401 (Unauthorized)**:
   - Clear localStorage: `localStorage.clear()`
   - Try to access any page
   - Should redirect to login
2. **Test 403 (Forbidden)**:
   - Login as Student
   - Try to access Admin-only page
   - Should show error or redirect
3. **Test 404 (Not Found)**:
   - Try to access non-existent resource
   - Should show "Resource not found" error
4. **Test 400 (Bad Request)**:
   - Submit invalid form data
   - Should show validation errors

### 4. UI/UX Testing

#### Test Responsive Design

1. Open browser DevTools
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test different screen sizes:
   - Mobile (375px)
   - Tablet (768px)
   - Desktop (1920px)
4. Verify:
   - Sidebar collapses on mobile
   - Tables are scrollable on small screens
   - Buttons are accessible

#### Test Loading States

1. Navigate to any list page
2. Check for loading spinner while data loads
3. Verify spinner disappears when data loads

#### Test Toast Notifications

1. Perform actions that trigger toasts:
   - Login success
   - API errors
   - Form submissions
2. Verify:
   - Toast appears in top-right corner
   - Toast auto-dismisses after 5 seconds
   - Toast has correct color (green for success, red for error)

#### Test Form Validation

1. Navigate to create/edit forms
2. Try submitting empty form
3. Should show validation errors
4. Fill required fields
5. Should allow submission

### 5. Browser Console Testing

Open Browser DevTools Console (F12) and check for:

1. **No JavaScript Errors**:

   - Should see no red error messages
   - Check for any warnings

2. **API Calls**:

   - Go to Network tab
   - Verify API calls are made correctly
   - Check request headers include `Authorization: Bearer <token>`
   - Verify response status codes

3. **Console Logs** (if any):
   - Check for helpful debug information

## Creating Test Data

### Using Django Admin

1. Access Django admin: `http://localhost:8000/admin`
2. Login with superuser credentials
3. Create test users for each role:
   - Student user
   - Instructor user
   - Admin user (or use superuser)
   - Registrar user

### Using Management Commands

```bash
# Seed database with test data
python scripts/seed_database.py

# Generate comprehensive test data
python scripts/generate_test_data.py
```

### Manual Test Data Creation

1. **Create Student**:

   - Login as Admin/Registrar
   - Navigate to Students > Add Student
   - Fill form and submit

2. **Create Course**:

   - Navigate to Courses > Create Course
   - Fill form and submit

3. **Create Class**:

   - Navigate to Classes > Create Class
   - Assign instructor, set schedule

4. **Enroll Student**:
   - Navigate to Enrollments
   - Create enrollment for student in class

## Common Issues & Troubleshooting

### Issue: CORS Errors

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**:

1. Check `CORS_ALLOWED_ORIGINS` in Django settings
2. Ensure frontend URL matches exactly (including port)
3. Restart Django server after changing CORS settings

### Issue: 401 Unauthorized

**Error**: `401 Unauthorized` on API calls

**Solutions**:

1. Check if token exists: `localStorage.getItem('sis_access_token')`
2. Verify token is included in request headers
3. Check if token is expired (default: 1 hour)
4. Try logging out and logging back in

### Issue: 403 Forbidden

**Error**: `403 Forbidden` on API calls

**Solution**:

1. Verify user has correct role
2. Check backend permissions
3. Ensure user is assigned proper role in database

### Issue: API Calls Not Working

**Check**:

1. Backend is running: `http://localhost:8000/api/v1/`
2. API base URL in `config.js` is correct
3. Network tab shows API calls being made
4. Check browser console for errors

### Issue: Pages Not Loading

**Check**:

1. File paths are correct (relative paths)
2. All JavaScript files are loaded (check Network tab)
3. No 404 errors for CSS/JS files
4. jQuery and Bootstrap are loaded

### Issue: Sidebar/Navbar Not Loading

**Check**:

1. jQuery `.load()` function is working
2. Component files exist in `components/` folder
3. Paths are correct (relative to page location)
4. Check browser console for errors

## Testing Checklist

### Authentication

- [ ] Login with valid credentials
- [ ] Login with invalid credentials (shows error)
- [ ] 2FA flow works (if enabled)
- [ ] Logout works
- [ ] Token stored in localStorage
- [ ] Auto-redirect on login
- [ ] Protected pages redirect to login when not authenticated

### Student Role

- [ ] Student dashboard loads
- [ ] Can view own profile
- [ ] Can view own enrollments
- [ ] Can view own grades
- [ ] Can view own attendance
- [ ] Can enroll in classes
- [ ] Cannot access admin pages

### Admin Role

- [ ] Admin dashboard loads
- [ ] Can view all students
- [ ] Can create/edit students
- [ ] Can manage courses
- [ ] Can manage classes
- [ ] Can manage users
- [ ] All pages accessible

### Instructor Role

- [ ] Instructor dashboard loads
- [ ] Can view assigned classes
- [ ] Can record attendance
- [ ] Can submit grades
- [ ] Cannot access student management

### UI/UX

- [ ] Responsive on mobile
- [ ] Responsive on tablet
- [ ] Responsive on desktop
- [ ] Loading spinners show
- [ ] Toast notifications work
- [ ] Forms validate correctly
- [ ] Tables paginate correctly
- [ ] Search/filter works

### API Integration

- [ ] All API calls include auth token
- [ ] Error handling works (401, 403, 400, 500)
- [ ] Token refresh works
- [ ] Pagination works
- [ ] Search works
- [ ] Filters work

## Automated Testing (Future)

For automated testing, consider:

1. **Selenium WebDriver**: For end-to-end testing
2. **Jest + Puppeteer**: For JavaScript testing
3. **Cypress**: For modern E2E testing
4. **Playwright**: For cross-browser testing

## Performance Testing

1. **Load Time**: Check page load times
2. **API Response**: Monitor API response times
3. **Large Datasets**: Test with 100+ students/courses
4. **Pagination**: Verify pagination works with large datasets

## Security Testing

1. **XSS**: Try injecting scripts in input fields
2. **CSRF**: Verify CSRF protection (if implemented)
3. **Token Security**: Verify tokens are not exposed in URLs
4. **Role Bypass**: Try accessing admin pages as student

## Browser Compatibility

Test in:

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

## Next Steps After Testing

1. Fix any bugs found
2. Improve error messages
3. Add loading states where missing
4. Optimize API calls
5. Add more validation
6. Improve responsive design

## Quick Test Script

Save this as `test-frontend.html` in frontend root:

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Frontend Test Page</title>
  </head>
  <body>
    <h1>Frontend Connection Test</h1>
    <button onclick="testConnection()">Test API Connection</button>
    <div id="result"></div>

    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="assets/js/config.js"></script>
    <script>
      function testConnection() {
        $.ajax({
          url: CONFIG.API_BASE_URL + "/auth/login/",
          method: "POST",
          contentType: "application/json",
          data: JSON.stringify({ username: "test", password: "test" }),
          success: function (response) {
            document.getElementById("result").innerHTML =
              '<p style="color: green;">✓ API is reachable!</p>';
          },
          error: function (xhr) {
            if (xhr.status === 400 || xhr.status === 401) {
              document.getElementById("result").innerHTML =
                '<p style="color: green;">✓ API is reachable! (Expected auth error)</p>';
            } else {
              document.getElementById("result").innerHTML =
                '<p style="color: red;">✗ API connection failed: ' +
                xhr.status +
                "</p>";
            }
          },
        });
      }
    </script>
  </body>
</html>
```

Open this file to quickly test if frontend can reach the backend API.
