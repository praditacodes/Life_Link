import random
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from .models import CustomUser
from django.utils import timezone
from geopy.geocoders import GoogleV3
import os

GOOGLE_API_KEY = os.environ.get('GOOGLE_GEOCODING_API_KEY', 'YOUR_API_KEY_HERE')
geolocator = GoogleV3(api_key=GOOGLE_API_KEY)

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp_via_email(email, otp):
    """Send OTP via email. Returns True if successful, else error message."""
    try:
        user = CustomUser.objects.get(email=email)
        subject = 'Blood Link - Email Verification Code'
        
        # HTML version of the email
        html_message = render_to_string('blood/email_otp_template.html', {
            'otp': otp,
            'app_name': 'Blood Link'
        })
        
        # Plain text version of the email
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except CustomUser.DoesNotExist:
        messages.error(request, 'No user found with this email address.')
        return False
    except Exception as e:
        return f"Error sending email: {str(e)}"

def is_otp_valid(otp_created_at):
    """Check if OTP is still valid (5 minutes)"""
    if not otp_created_at:
        return False
    return timezone.now() - otp_created_at < timedelta(minutes=5) 