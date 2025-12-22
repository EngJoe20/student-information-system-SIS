# AcademiaHub Frontend - Architecture Documentation

## Frontend Architecture Design

### Technology Stack
- **HTML5**: Semantic markup
- **CSS3**: Styling and animations
- **Bootstrap 5**: Responsive UI framework
- **JavaScript (ES6+)**: Core logic
- **jQuery 3.6+**: DOM manipulation and AJAX
- **AJAX**: RESTful API communication

### Folder Structure

```
frontend/
├── index.html                 # Landing/Login page
├── assets/
│   ├── css/
│   │   ├── main.css          # Custom styles
│   │   ├── auth.css          # Authentication styles
│   │   └── dashboard.css     # Dashboard styles
│   ├── js/
│   │   ├── config.js         # API configuration
│   │   ├── auth.js           # Authentication logic
│   │   ├── api.js            # API wrapper functions
│   │   ├── utils.js          # Utility functions
│   │   └── main.js           # Main application logic
│   └── images/               # Static images
├── pages/
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── dashboard/
│   │   ├── admin.html
│   │   ├── student.html
│   │   ├── instructor.html
│   │   └── registrar.html
│   ├── students/
│   │   ├── list.html
│   │   ├── create.html
│   │   ├── view.html
│   │   └── edit.html
│   ├── courses/
│   │   ├── list.html
│   │   ├── create.html
│   │   ├── view.html
│   │   └── edit.html
│   ├── classes/
│   │   ├── list.html
│   │   ├── create.html
│   │   ├── view.html
│   │   └── timetable.html
│   ├── enrollments/
│   │   ├── list.html
│   │   └── create.html
│   ├── attendance/
│   │   ├── list.html
│   │   ├── record.html
│   │   └── bulk-record.html
│   ├── grades/
│   │   ├── list.html
│   │   ├── submit.html
│   │   └── statistics.html
│   ├── notifications/
│   │   └── list.html
│   ├── messages/
│   │   ├── inbox.html
│   │   ├── sent.html
│   │   └── compose.html
│   └── requests/
│       ├── list.html
│       └── create.html
└── components/
    ├── navbar.html           # Reusable navbar component
    ├── sidebar.html          # Reusable sidebar component
    └── footer.html           # Reusable footer component
```

## Architecture Justification

### 1. **Separation of Concerns**
- **HTML**: Structure and content
- **CSS**: Presentation and styling
- **JavaScript**: Behavior and logic
- **jQuery**: DOM manipulation and AJAX

### 2. **Modular Design**
- **Pages**: Each feature has its own HTML file
- **Components**: Reusable UI elements (navbar, sidebar)
- **Assets**: Organized by type (CSS, JS, images)

### 3. **API Integration**
- **config.js**: Centralized API base URL and configuration
- **api.js**: Wrapper functions for all API endpoints
- **auth.js**: JWT token management and authentication flow

### 4. **Role-Based Access**
- **Dashboard routing**: Different dashboards per role
- **UI visibility**: Show/hide elements based on user role
- **API permissions**: Client-side validation before API calls

### 5. **State Management**
- **localStorage**: Store JWT tokens and user data
- **Session management**: Token refresh and expiration handling
- **User context**: Current user role and permissions

## Key Features

### Authentication Flow
1. User logs in → JWT tokens stored in localStorage
2. All API requests include `Authorization: Bearer <token>` header
3. Token refresh on 401 errors
4. Redirect to login on authentication failure

### Role-Based Routing
- **Admin**: Full access to all modules
- **Student**: Limited to own data and enrollment
- **Instructor**: Classes, attendance, grades for assigned classes
- **Registrar**: Student management, enrollment, reports

### Error Handling
- **401**: Redirect to login
- **403**: Show permission denied message
- **400**: Display validation errors
- **500**: Show generic error message

### UI/UX Features
- **Responsive design**: Bootstrap 5 grid system
- **Loading indicators**: Show during API calls
- **Toast notifications**: Success/error messages
- **Pagination**: For list views
- **Search & Filter**: Query parameter-based filtering
- **Form validation**: Client-side validation before submission

## API Integration Pattern

All API calls follow this pattern:
```javascript
// 1. Get token from localStorage
const token = localStorage.getItem('access_token');

// 2. Make AJAX request with Authorization header
$.ajax({
    url: API_BASE_URL + '/endpoint',
    method: 'GET',
    headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    },
    success: function(response) {
        // Handle success
    },
    error: function(xhr) {
        // Handle error (401, 403, 400, etc.)
    }
});
```

## Security Considerations

1. **Token Storage**: localStorage (consider httpOnly cookies for production)
2. **HTTPS**: Required in production
3. **XSS Protection**: Sanitize user inputs
4. **CSRF**: Django handles CSRF tokens
5. **Role Validation**: Client-side UI control + server-side API validation

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development Workflow

1. **Local Development**: Serve static files via Django or simple HTTP server
2. **API Connection**: Point to `http://localhost:8000/api/v1/`
3. **Testing**: Test with different user roles
4. **Production**: Deploy static files to CDN or Django static files

