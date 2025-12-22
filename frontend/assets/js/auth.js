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
 * Get stored temp token (for 2FA flow)
 */
function getTempToken() {
    return localStorage.getItem(CONFIG.TEMP_TOKEN_KEY);
}

/**
 * Store temp token (for 2FA flow)
 */
function setTempToken(tempToken) {
    localStorage.setItem(CONFIG.TEMP_TOKEN_KEY, tempToken);
}

/**
 * Clear authentication data
 */
function clearAuthData() {
    localStorage.removeItem(CONFIG.TOKEN_KEY);
    localStorage.removeItem(CONFIG.REFRESH_TOKEN_KEY);
    localStorage.removeItem(CONFIG.TEMP_TOKEN_KEY);
    localStorage.removeItem(CONFIG.USER_KEY);
}

/**
 * Check if user is authenticated (has valid JWT tokens)
 * Returns false if only temp token exists (2FA not completed)
 */
function isAuthenticated() {
    const accessToken = getAccessToken();
    const tempToken = getTempToken();
    
    // If we have a temp token but no access token, 2FA is not completed
    if (tempToken && !accessToken) {
        return false;
    }
    
    return accessToken !== null;
}

/**
 * Check if user is in 2FA flow (has temp token but no access token)
 */
function isIn2FAFlow() {
    return getTempToken() !== null && getAccessToken() === null;
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
        return Promise.reject(new Error('No refresh token available'));
    }
    
    return $.ajax({
        url: CONFIG.API_BASE_URL + '/auth/refresh/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ refresh_token: refreshToken }),
        success: function(response) {
            if (response.status === 'success' && response.data.access_token) {
                // Update access token, keep refresh token and user data
                localStorage.setItem(CONFIG.TOKEN_KEY, response.data.access_token);
                if (response.data.refresh_token) {
                    localStorage.setItem(CONFIG.REFRESH_TOKEN_KEY, response.data.refresh_token);
                }
                return response.data.access_token;
            }
            throw new Error('Failed to refresh token');
        },
        error: function(xhr) {
            // Refresh token is invalid or expired
            clearAuthData();
            const response = xhr.responseJSON;
            const errorMsg = response?.message || 'Session expired. Please login again.';
            
            // Don't redirect immediately if we're on login page
            if (!window.location.pathname.includes('login.html')) {
                showToast(errorMsg, 'error');
                setTimeout(() => {
                    window.location.href = CONFIG.ROUTES.LOGIN;
                }, 2000);
            }
            throw new Error(errorMsg);
        }
    });
}

/**
 * Handle API error responses
 * Note: This should NOT be called for 2FA-related endpoints during login flow
 */
function handleApiError(xhr) {
    // Don't handle errors on login/2FA pages - let them handle their own errors
    if (window.location.pathname.includes('login.html')) {
        return;
    }
    
    if (xhr.status === 401) {
        // Unauthorized - try to refresh token
        // Only attempt refresh if we have a refresh token and are not in 2FA flow
        if (getRefreshToken() && !isIn2FAFlow()) {
            refreshAccessToken()
                .then(() => {
                    // Token refreshed - user can retry the action
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
        } else {
            // No refresh token or in 2FA flow - redirect to login
            clearAuthData();
            showToast('Authentication required. Please login.', 'error');
            setTimeout(() => {
                window.location.href = CONFIG.ROUTES.LOGIN;
            }, 2000);
        }
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
            showToast(response?.message || 'Invalid request', 'error');
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
        statusCode: {
            200: function(response) {
                // Normal login success
                if (response.status === 'success') {
                    setAuthData(
                        response.data.access_token,
                        response.data.refresh_token,
                        response.data.user
                    );
                    return response;
                }
                throw new Error(response.message || 'Login failed');
            },
            202: function(response) {
                // 2FA required - HTTP 202 Accepted
                if (response.status === '2fa_required') {
                    // Store temp token for 2FA verification
                    if (response.temp_token) {
                        setTempToken(response.temp_token);
                    }
                    return response;
                }
                throw new Error(response.message || '2FA required but temp token missing');
            }
        },
        success: function(response) {
            // Fallback for any 2xx status
            if (response.status === 'success') {
                setAuthData(
                    response.data.access_token,
                    response.data.refresh_token,
                    response.data.user
                );
                return response;
            } else if (response.status === '2fa_required') {
                if (response.temp_token) {
                    setTempToken(response.temp_token);
                }
                return response;
            }
            throw new Error(response.message || 'Login failed');
        },
        error: function(xhr) {
            // Handle non-2xx responses
            const response = xhr.responseJSON;
            if (xhr.status === 400 || xhr.status === 401) {
                // Invalid credentials
                throw new Error(response?.message || 'Invalid username or password');
            }
            handleApiError(xhr);
            throw new Error('Login failed');
        }
    });
}

/**
 * Verify 2FA
 */
function verify2FA(tempToken, otpCode) {
    // Use temp token from parameter or localStorage
    const token = tempToken || getTempToken();
    
    if (!token) {
        return Promise.reject(new Error('No temporary token found. Please login again.'));
    }
    
    return $.ajax({
        url: CONFIG.API_BASE_URL + '/auth/verify-2fa/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ temp_token: token, otp_code: otpCode }),
        success: function(response) {
            if (response.status === 'success') {
                // Clear temp token and store JWT tokens
                localStorage.removeItem(CONFIG.TEMP_TOKEN_KEY);
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
            const response = xhr.responseJSON;
            
            // Handle specific error cases
            if (xhr.status === 400) {
                if (response?.code === 'INVALID_TOKEN' || response?.message?.includes('expired')) {
                    // Temp token expired - clear it and redirect to login
                    clearAuthData();
                    throw new Error('Temporary token expired. Please login again.');
                } else if (response?.code === 'INVALID_OTP' || response?.message?.includes('OTP')) {
                    // Invalid OTP code
                    throw new Error('Invalid OTP code. Please try again.');
                }
                throw new Error(response?.message || 'Invalid request');
            }
            
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
    
    // Always clear local data first
    clearAuthData();
    
    // Try to invalidate refresh token on server (non-blocking)
    if (refreshToken) {
        $.ajax({
            url: CONFIG.API_BASE_URL + '/auth/logout/',
            method: 'POST',
            contentType: 'application/json',
            headers: getAuthHeader(),
            data: JSON.stringify({ refresh_token: refreshToken }),
            timeout: 3000, // 3 second timeout
            error: function() {
                // Continue with logout even if API call fails
                console.error('Logout API call failed (non-critical)');
            },
            complete: function() {
                // Redirect after attempting server logout
                window.location.href = CONFIG.ROUTES.LOGIN;
            }
        });
    } else {
        // No refresh token, just redirect
        window.location.href = CONFIG.ROUTES.LOGIN;
    }
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
    // If user has temp token but no access token, they're in 2FA flow
    if (isIn2FAFlow()) {
        // Redirect to login to complete 2FA
        showToast('Please complete 2FA verification', 'info');
        window.location.href = CONFIG.ROUTES.LOGIN;
        return false;
    }
    
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

