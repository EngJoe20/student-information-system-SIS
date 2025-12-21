"""
Core utility functions used across the application.
"""
import secrets
import pyotp
import qrcode
from io import BytesIO
import base64
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def generate_reset_token():
    """Generate secure password reset token."""
    return secrets.token_urlsafe(32)


def generate_otp_secret():
    """Generate OTP secret for 2FA."""
    return pyotp.random_base32()


def verify_otp(secret, otp_code):
    """Verify OTP code against secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(otp_code, valid_window=1)


def generate_qr_code(user, secret):
    """Generate QR code for 2FA setup."""
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email,
        issuer_name='SIS - Student Information System'
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Extract user agent from request."""
    return request.META.get('HTTP_USER_AGENT', '')[:500]


def send_email_notification(to_email, subject, template_name, context):
    """Send email notification using template."""
    try:
        html_message = render_to_string(f'emails/{template_name}', context)
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False


def create_password_reset_link(token):
    """Create password reset link."""
    return f"{settings.FRONTEND_URL}/reset-password?token={token}"


class StandardResponse:
    """Standardize API responses."""
    
    @staticmethod
    def success(data=None, message=None):
        """Success response format."""
        response = {"status": "success"}
        if message:
            response["message"] = message
        if data is not None:
            response["data"] = data
        return response
    
    @staticmethod
    def error(message, code=None, errors=None):
        """Error response format."""
        response = {
            "status": "error",
            "message": message,
        }
        if code:
            response["code"] = code
        if errors:
            response["errors"] = errors
        response["timestamp"] = timezone.now().isoformat()
        return response
    
    @staticmethod
    def requires_2fa(temp_token):
        """2FA required response."""
        return {
            "status": "2fa_required",
            "message": "Please provide OTP code",
            "temp_token": temp_token
        }