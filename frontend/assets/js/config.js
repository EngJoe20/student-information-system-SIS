/**
 * Academia Frontend - Configuration
 * API endpoints and application settings
 */

const CONFIG = {
    // API Configuration
    API_BASE_URL: 'http://localhost:8000/api/v1',
    
    // Token keys
    TOKEN_KEY: 'sis_access_token',
    REFRESH_TOKEN_KEY: 'sis_refresh_token',
    TEMP_TOKEN_KEY: 'sis_temp_token',
    USER_KEY: 'sis_user',
    
    // Pagination
    DEFAULT_PAGE_SIZE: 20,
    
    // Date formats
    DATE_FORMAT: 'YYYY-MM-DD',
    DATETIME_FORMAT: 'YYYY-MM-DDTHH:mm:ssZ',
    
    // Roles
    ROLES: {
        ADMIN: 'ADMIN',
        STUDENT: 'STUDENT',
        INSTRUCTOR: 'INSTRUCTOR',
        REGISTRAR: 'REGISTRAR'
    },
    
    // Routes
    ROUTES: {
        LOGIN: '/frontend/pages/auth/login.html',
        ADMIN_DASHBOARD: '/frontend/pages/dashboard/admin.html',
        STUDENT_DASHBOARD: '/frontend/pages/dashboard/student.html',
        INSTRUCTOR_DASHBOARD: '/frontend/pages/dashboard/instructor.html',
        REGISTRAR_DASHBOARD: '/frontend/pages/dashboard/registrar.html'
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}

