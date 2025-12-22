/**
 * SIS Frontend - Authentication Module
 * Handles JWT authentication, token management, and user session
 */

/**
 * Get stored access token
 */
function getAccessToken() {
    return localStorage.getItem(CONFIG.TOKEN_KEY);
}

/**
 * Get stored refresh token
 */
function getRefreshToken() {
    return localStorage.getItem(CONFIG.REFRESH_TOKEN_KEY);
}

/**
 * Get stored user data
 */
function getCurrentUser() {
    const userStr = localStorage.getItem(CONFIG.USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
}

/**
 * Store authentication tokens and user data
 */
function setAuthData(accessToken, refreshToken, user) {
    localStorage.setItem(CONFIG.TOKEN_KEY, accessToken);
    localStorage.setItem(CONFIG.REFRESH_TOKEN_KEY, refreshToken);
    localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(user));
}

/**
 * Clear authentication data
 */
function clearAuthData() {
    localStorage.removeItem(CONFIG.TOKEN_KEY);
    localStorage.removeItem(CONFIG.REFRESH_TOKEN_KEY);
    localStorage.removeItem(CONFIG.USER_KEY);
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return getAccessToken() !== null;
}

/**
 * Get authorization header
 */
function getAuthHeader() {
    const token = getAccessToken();
    return token ? { 'Authorization': 'Bearer ' + token } : {};
}

/**
 * Refresh access token
 */
function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        return Promise.reject('No refresh token available');
    }
    
    return $.ajax({
        url: CONFIG.API_BASE_URL + '/auth/refresh/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ refresh_token: refreshToken }),
        success: function(response) {
            if (response.status === 'success' && response.data.access_token) {
                localStorage.setItem(CONFIG.TOKEN_KEY, response.data.access_token);
                return response.data.access_token;
            }
            throw new Error('Failed to refresh token');
        },
        error: function() {
            clearAuthData();
            window.location.href = CONFIG.ROUTES.LOGIN;
            throw new Error('Token refresh failed');
        }
    });
}

/**
 * Handle API error responses
 */
function handleApiError(xhr) {
    if (xhr.status === 401) {
        // Try to refresh token
        refreshAccessToken()
            .then(() => {
                // Retry the original request
                showToast('Session refreshed. Please try again.', 'info');
            })
            .catch(() => {
                // Refresh failed, redirect to login
                clearAuthData();
                showToast('Session expired. Please login again.', 'error');
                setTimeout(() => {
                    window.location.href = CONFIG.ROUTES.LOGIN;
                }, 2000);
            });
    } else if (xhr.status === 403) {
        showToast('You do not have permission to perform this action.', 'error');
    } else if (xhr.status === 400) {
        const response = xhr.responseJSON;
        if (response && response.errors) {
            // Display validation errors
            let errorMsg = 'Validation errors:\n';
            for (const field in response.errors) {
                errorMsg += `${field}: ${response.errors[field].join(', ')}\n`;
            }
            showToast(errorMsg, 'error');
        } else {
            showToast(response.message || 'Invalid request', 'error');
        }
    } else if (xhr.status === 404) {
        showToast('Resource not found', 'error');
    } else if (xhr.status >= 500) {
        showToast('Server error. Please try again later.', 'error');
    } else {
        const response = xhr.responseJSON;
        showToast(response?.message || 'An error occurred', 'error');
    }
}

/**
 * Login user
 */
function login(username, password) {
    return $.ajax({
        url: CONFIG.API_BASE_URL + '/auth/login/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ username, password }),
        success: function(response) {
            if (response.status === 'success') {
                setAuthData(
                    response.data.access_token,
                    response.data.refresh_token,
                    response.data.user
                );
                return response;
            } else if (response.status === '2fa_required') {
                // Handle 2FA requirement
                return response;
            }
            throw new Error(response.message || 'Login failed');
        },
        error: function(xhr) {
            handleApiError(xhr);
            throw new Error('Login failed');
        }
    });
}

/**
 * Verify 2FA
 */
function verify2FA(tempToken, otpCode) {
    return $.ajax({
        url: CONFIG.API_BASE_URL + '/auth/verify-2fa/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ temp_token: tempToken, otp_code: otpCode }),
        success: function(response) {
            if (response.status === 'success') {
                setAuthData(
                    response.data.access_token,
                    response.data.refresh_token,
                    response.data.user
                );
                return response;
            }
            throw new Error(response.message || '2FA verification failed');
        },
        error: function(xhr) {
            handleApiError(xhr);
            throw new Error('2FA verification failed');
        }
    });
}

/**
 * Logout user
 */
function logout() {
    const refreshToken = getRefreshToken();
    
    if (refreshToken) {
        $.ajax({
            url: CONFIG.API_BASE_URL + '/auth/logout/',
            method: 'POST',
            contentType: 'application/json',
            headers: getAuthHeader(),
            data: JSON.stringify({ refresh_token: refreshToken }),
            error: function() {
                // Continue with logout even if API call fails
                console.error('Logout API call failed');
            }
        });
    }
    
    clearAuthData();
    window.location.href = CONFIG.ROUTES.LOGIN;
}

/**
 * Request password reset
 */
function requestPasswordReset(email) {
    return $.ajax({
        url: CONFIG.API_BASE_URL + '/auth/password-reset/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ email }),
        success: function(response) {
            return response;
        },
        error: function(xhr) {
            handleApiError(xhr);
            throw new Error('Password reset request failed');
        }
    });
}

/**
 * Confirm password reset
 */
function confirmPasswordReset(token, newPassword, confirmPassword) {
    return $.ajax({
        url: CONFIG.API_BASE_URL + '/auth/password-reset-confirm/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            token,
            new_password: newPassword,
            confirm_password: confirmPassword
        }),
        success: function(response) {
            return response;
        },
        error: function(xhr) {
            handleApiError(xhr);
            throw new Error('Password reset failed');
        }
    });
}

/**
 * Check authentication and redirect if needed
 */
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = CONFIG.ROUTES.LOGIN;
        return false;
    }
    return true;
}

/**
 * Check role and redirect if needed
 */
function requireRole(requiredRoles) {
    if (!requireAuth()) return false;
    
    const user = getCurrentUser();
    if (!user) {
        window.location.href = CONFIG.ROUTES.LOGIN;
        return false;
    }
    
    if (!hasPermission(user.role, requiredRoles)) {
        showToast('You do not have permission to access this page.', 'error');
        redirectByRole(user.role);
        return false;
    }
    
    return true;
}

