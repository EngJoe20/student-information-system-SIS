/**
 * SIS Frontend - Utility Functions
 * Common helper functions used across the application
 */

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const toastContainer = $('#toast-container');
    if (toastContainer.length === 0) {
        $('body').append('<div id="toast-container" class="position-fixed top-0 end-0 p-3" style="z-index: 9999;"></div>');
    }
    
    const bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast ${bgClass} text-white" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${bgClass} text-white">
                <strong class="me-auto">${type === 'success' ? 'Success' : type === 'error' ? 'Error' : 'Info'}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">${message}</div>
        </div>
    `;
    
    $('#toast-container').append(toastHtml);
    const toastElement = new bootstrap.Toast(document.getElementById(toastId), {
        autohide: true,
        delay: 5000
    });
    toastElement.show();
    
    // Remove toast element after it's hidden
    $(`#${toastId}`).on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

/**
 * Show loading spinner
 */
function showLoading(element) {
    const loadingHtml = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    $(element).html(loadingHtml);
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Format datetime for display
 */
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Format percentage
 */
function formatPercentage(value, decimals = 2) {
    return parseFloat(value).toFixed(decimals) + '%';
}

/**
 * Get query parameter from URL
 */
function getQueryParam(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

/**
 * Set query parameter in URL
 */
function setQueryParam(name, value) {
    const url = new URL(window.location);
    url.searchParams.set(name, value);
    window.history.pushState({}, '', url);
}

/**
 * Remove query parameter from URL
 */
function removeQueryParam(name) {
    const url = new URL(window.location);
    url.searchParams.delete(name);
    window.history.pushState({}, '', url);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate UUID format
 */
function isValidUUID(uuid) {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    return uuidRegex.test(uuid);
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    text = String(text);
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}


/**
 * Truncate text
 */
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Get role display name
 */
function getRoleDisplayName(role) {
    const roleMap = {
        'ADMIN': 'Administrator',
        'STUDENT': 'Student',
        'INSTRUCTOR': 'Instructor',
        'REGISTRAR': 'Registrar'
    };
    return roleMap[role] || role;
}

/**
 * Get status badge HTML
 */
function getStatusBadge(status, type = 'default') {
    const badgeClass = {
        'ACTIVE': 'bg-success',
        'SUSPENDED': 'bg-danger',
        'GRADUATED': 'bg-info',
        'WITHDRAWN': 'bg-warning',
        'ENROLLED': 'bg-primary',
        'DROPPED': 'bg-secondary',
        'COMPLETED': 'bg-success',
        'FAILED': 'bg-danger',
        'PENDING': 'bg-warning',
        'APPROVED': 'bg-success',
        'REJECTED': 'bg-danger',
        'IN_PROGRESS': 'bg-info',
        'OPEN': 'bg-success',
        'CLOSED': 'bg-secondary',
        'CANCELLED': 'bg-danger',
        'PRESENT': 'bg-success',
        'ABSENT': 'bg-danger',
        'LATE': 'bg-warning',
        'EXCUSED': 'bg-info'
    };
    
    const className = badgeClass[status] || 'bg-secondary';
    return `<span class="badge ${className}">${status}</span>`;
}

/**
 * Format GPA
 */
function formatGPA(gpa) {
    if (gpa === null || gpa === undefined) return 'N/A';
    return parseFloat(gpa).toFixed(2);
}

/**
 * Check if user has permission
 */
function hasPermission(userRole, requiredRoles) {
    if (!Array.isArray(requiredRoles)) {
        requiredRoles = [requiredRoles];
    }
    return requiredRoles.includes(userRole);
}

/**
 * Redirect based on user role
 */
function redirectByRole(role) {
    const routes = CONFIG.ROUTES;
    switch(role) {
        case CONFIG.ROLES.ADMIN:
            window.location.href = routes.ADMIN_DASHBOARD;
            break;
        case CONFIG.ROLES.STUDENT:
            window.location.href = routes.STUDENT_DASHBOARD;
            break;
        case CONFIG.ROLES.INSTRUCTOR:
            window.location.href = routes.INSTRUCTOR_DASHBOARD;
            break;
        case CONFIG.ROLES.REGISTRAR:
            window.location.href = routes.REGISTRAR_DASHBOARD;
            break;
        default:
            window.location.href = routes.LOGIN;
    }
}

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize popovers
 */
function initPopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Initialize on document ready
$(document).ready(function() {
    initTooltips();
    initPopovers();
});

