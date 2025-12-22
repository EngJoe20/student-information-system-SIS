/**
 * SIS Frontend - API Wrapper Functions
 * Centralized API calls for all endpoints
 */

/**
 * Generic API request function
 */
function apiRequest(url, method = 'GET', data = null, options = {}) {
    const defaultOptions = {
        url: CONFIG.API_BASE_URL + url,
        method: method,
        contentType: 'application/json',
        headers: {
            ...getAuthHeader(),
            ...(options.headers || {})
        },
        data: data ? JSON.stringify(data) : null,
        ...options
    };
    
    // Handle file uploads
    if (options.isFileUpload) {
        delete defaultOptions.contentType;
        defaultOptions.processData = false;
        defaultOptions.contentType = false;
        defaultOptions.data = data;
    }
    
    return $.ajax(defaultOptions)
        .fail(function(xhr) {
            // Only handle errors if not in auth flow (login/2FA pages handle their own errors)
            if (!window.location.pathname.includes('login.html')) {
                handleApiError(xhr);
            }
            throw xhr;
        });
}

// ==================== AUTHENTICATION API ====================

const AuthAPI = {
    login: (username, password) => login(username, password),
    verify2FA: (tempToken, otpCode) => verify2FA(tempToken, otpCode),
    logout: () => logout(),
    refreshToken: () => refreshAccessToken(),
    requestPasswordReset: (email) => requestPasswordReset(email),
    confirmPasswordReset: (token, newPassword, confirmPassword) => 
        confirmPasswordReset(token, newPassword, confirmPassword)
};

// ==================== USER API ====================

const UserAPI = {
    list: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest('/users/?' + queryString);
    },
    get: (id) => apiRequest(`/users/${id}/`),
    create: (data) => apiRequest('/users/', 'POST', data),
    update: (id, data) => apiRequest(`/users/${id}/`, 'PUT', data),
    delete: (id) => apiRequest(`/users/${id}/`, 'DELETE'),
    getCurrent: () => apiRequest('/users/me/'),
    assignRole: (id, role) => apiRequest(`/users/${id}/assign-role/`, 'POST', { role }),
    enable2FA: () => apiRequest('/users/enable-2fa/', 'POST', {}),
    verify2FASetup: (otpSecret, otpCode) => 
        apiRequest('/users/verify-2fa-setup/', 'POST', { otp_secret: otpSecret, otp_code: otpCode }),
    disable2FA: () => apiRequest('/users/disable-2fa/', 'POST', {})
};

// ==================== STUDENT API ====================

const StudentAPI = {
    list: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest('/students/?' + queryString);
    },
    get: (id) => apiRequest(`/students/${id}/`),
    create: (data) => apiRequest('/students/', 'POST', data),
    update: (id, data) => apiRequest(`/students/${id}/`, 'PUT', data),
    delete: (id) => apiRequest(`/students/${id}/`, 'DELETE'),
    getEnrollments: (id, params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest(`/students/${id}/enrollments/?` + queryString);
    },
    getAttendance: (id, params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest(`/students/${id}/attendance/?` + queryString);
    },
    getGrades: (id, params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest(`/students/${id}/grades/?` + queryString);
    },
    getTranscript: (id) => apiRequest(`/students/${id}/transcript/`)
};

// ==================== ENROLLMENT API ====================

const EnrollmentAPI = {
    list: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest('/enrollments/?' + queryString);
    },
    get: (id) => apiRequest(`/enrollments/${id}/`),
    create: (data) => apiRequest('/enrollments/', 'POST', data),
    delete: (id) => apiRequest(`/enrollments/${id}/`, 'DELETE')
};

// ==================== COURSE API ====================

const CourseAPI = {
    list: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest('/courses/?' + queryString);
    },
    get: (id) => apiRequest(`/courses/${id}/`),
    create: (data) => apiRequest('/courses/', 'POST', data),
    update: (id, data) => apiRequest(`/courses/${id}/`, 'PUT', data),
    delete: (id) => apiRequest(`/courses/${id}/`, 'DELETE')
};

// ==================== CLASS API ====================

const ClassAPI = {
    list: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest('/classes/?' + queryString);
    },
    get: (id) => apiRequest(`/classes/${id}/`),
    create: (data) => apiRequest('/classes/', 'POST', data),
    update: (id, data) => apiRequest(`/classes/${id}/`, 'PUT', data),
    getTimetable: (params) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest('/classes/timetable/?' + queryString);
    },
    getAttendance: (id, params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest(`/classes/${id}/attendance/?` + queryString);
    },
    getRoster: (id) => apiRequest(`/classes/${id}/roster/`)
};

// ==================== ATTENDANCE API ====================

const AttendanceAPI = {
    list: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest('/attendance/?' + queryString);
    },
    get: (id) => apiRequest(`/attendance/${id}/`),
    create: (data) => apiRequest('/attendance/', 'POST', data),
    update: (id, data) => apiRequest(`/attendance/${id}/`, 'PUT', data),
    bulkRecord: (data) => apiRequest('/attendance/bulk-record/', 'POST', data),
    getStudentAttendance: (studentId, params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest(`/attendance/student/${studentId}/?` + queryString);
    },
    getClassAttendance: (classId, params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest(`/attendance/class/${classId}/?` + queryString);
    }
};

// ==================== GRADE API ====================

const GradeAPI = {
    list: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest('/grades/?' + queryString);
    },
    get: (id) => apiRequest(`/grades/${id}/`),
    create: (data) => apiRequest('/grades/', 'POST', data),
    update: (id, data) => apiRequest(`/grades/${id}/`, 'PUT', data),
    getStudentGrades: (studentId, params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest(`/grades/student/${studentId}/?` + queryString);
    },
    finalizeGrade: (enrollmentId, finalGrade) => 
        apiRequest(`/grades/enrollment/${enrollmentId}/finalize/`, 'POST', { final_grade: finalGrade }),
    getClassStatistics: (classId) => apiRequest(`/grades/class/${classId}/statistics/`)
};

// ==================== ROOM API ====================

const RoomAPI = {
    list: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest('/rooms/?' + queryString);
    },
    get: (id) => apiRequest(`/rooms/${id}/`),
    create: (data) => apiRequest('/rooms/', 'POST', data),
    update: (id, data) => apiRequest(`/rooms/${id}/`, 'PUT', data),
    delete: (id) => apiRequest(`/rooms/${id}/`, 'DELETE'),
    getAvailable: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest('/rooms/available/?' + queryString);
    }
};

// ==================== EXAM API ====================

const ExamAPI = {
    list: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest('/exams/?' + queryString);
    },
    get: (id) => apiRequest(`/exams/${id}/`),
    create: (data) => apiRequest('/exams/', 'POST', data),
    update: (id, data) => apiRequest(`/exams/${id}/`, 'PUT', data)
};

// ==================== NOTIFICATION API ====================

const NotificationAPI = {
    list: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest('/notifications/?' + queryString);
    },
    markRead: (id) => apiRequest(`/notifications/${id}/mark-read/`, 'PUT'),
    markAllRead: () => apiRequest('/notifications/mark-all-read/', 'POST'),
    delete: (id) => apiRequest(`/notifications/${id}/`, 'DELETE')
};

// ==================== MESSAGE API ====================

const MessageAPI = {
    list: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest('/messages/?' + queryString);
    },
    get: (id) => apiRequest(`/messages/${id}/`),
    create: (data) => apiRequest('/messages/', 'POST', data),
    delete: (id) => apiRequest(`/messages/${id}/`, 'DELETE')
};

// ==================== STUDENT REQUEST API ====================

const StudentRequestAPI = {
    list: (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest('/student-requests/?' + queryString);
    },
    get: (id) => apiRequest(`/student-requests/${id}/`),
    create: (data) => apiRequest('/student-requests/', 'POST', data),
    update: (id, data) => apiRequest(`/student-requests/${id}/`, 'PUT', data)
};

// ==================== REPORT API ====================

const ReportAPI = {
    getTranscript: (studentId, format = 'pdf') => {
        return apiRequest(`/reports/transcript/${studentId}/?format=${format}`, 'GET', null, {
            responseType: format === 'pdf' ? 'blob' : 'json'
        });
    },
    generateAttendanceReport: (data) => apiRequest('/reports/attendance/', 'POST', data),
    generateGradeReport: (data) => apiRequest('/reports/grades/', 'POST', data)
};

// ==================== DASHBOARD API ====================

const DashboardAPI = {
    getAdmin: () => apiRequest('/dashboard/admin/'),
    getStudent: () => apiRequest('/dashboard/student/'),
    getInstructor: () => apiRequest('/dashboard/instructor/')
};

