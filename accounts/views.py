from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .models import Profile
from django.contrib import messages
from blood.forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.utils import timezone
from .forms import OTPVerificationForm
import random
from blood.models import CustomUser
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.shortcuts import redirect

User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        
        # Check if both forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            # Show error messages for invalid forms
            if not user_form.is_valid():
                for field, errors in user_form.errors.items():
                    for error in errors:
                        messages.error(request, f'User form error: {error}')
            if not profile_form.is_valid():
                for field, errors in profile_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Profile form error: {error}')
    else:
        user_form = CustomUserCreationForm()
        profile_form = ProfileForm()
    
    return render(request, 'accounts/register.html', {
        'user_form': user_form, 
        'profile_form': profile_form
    })

@login_required
def profile_update_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile = profile_form.save()
            # Automatic geocoding
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="life_link_geocode")
            address_parts = [
                profile.address or '',
                profile.city or '',
                profile.state or '',
                profile.pincode or ''
            ]
            address_str = ', '.join([part for part in address_parts if part])
            try:
                if address_str.strip():
                    location = geolocator.geocode(address_str)
                    if location:
                        profile.latitude = location.latitude
                        profile.longitude = location.longitude
                        profile.save()
            except Exception as e:
                print(f"Geocoding error: {e}")
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        profile_form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile.html', {'profile_form': profile_form})

@login_required
def user_dashboard_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.user.is_superuser:
        return render(request, 'blood/admin_dashboard.html')

    # Fetch recent donations and requests
    from donor.models import BloodDonate
    from blood.models import BloodRequest
    donations = BloodDonate.objects.filter(donor=profile).order_by('-date')[:5]
    requests = BloodRequest.objects.filter(requested_by=profile).order_by('-date')[:5]
    # Combine and sort by date
    recent_activity = []
    for d in donations:
        recent_activity.append({
            'type': 'Donation',
            'blood_group': d.bloodgroup,
            'unit': d.unit,
            'date': d.date,
            'status': d.status,
        })
    for r in requests:
        recent_activity.append({
            'type': 'Request',
            'blood_group': r.blood_group,
            'unit': r.unit,
            'date': r.date,
            'status': r.status,
        })
    # Sort all by date descending
    recent_activity = sorted(recent_activity, key=lambda x: x['date'], reverse=True)[:5]
    # Stats
    donation_count = BloodDonate.objects.filter(donor=profile, status='Approved').count()
    request_count = BloodRequest.objects.filter(requested_by=profile).count()
    return render(request, 'accounts/dashboard.html', {
        'profile': profile,
        'recent_activity': recent_activity,
        'donation_count': donation_count,
        'request_count': request_count,
    })

def send_otp_via_email(user):
    otp = str(random.randint(100000, 999999))
    user.otp = otp
    user.otp_created_at = timezone.now()
    user.save()
    send_mail(
        'Your Life-Link Login OTP',
        f'Your OTP for login is: {otp}',
        'praditabadal5@gmail.com',  # From email (should match EMAIL_HOST_USER)
        [user.email],
        fail_silently=False,
    )

def custom_login_view(request):
    if request.method == 'POST':
        if 'step' in request.POST and request.POST['step'] == 'otp':
            # Step 2: Validate OTP
            username = request.session.get('otp_username')
            user = CustomUser.objects.filter(username=username).first()
            form = OTPVerificationForm(request.POST)
            if user and form.is_valid():
                otp = form.cleaned_data['otp']
                if user.otp == otp and user.otp_created_at and (timezone.now() - user.otp_created_at).seconds < 600:
                    user.is_phone_verified = True
                    user.otp = None
                    user.otp_created_at = None
                    user.save()
                    login(request, user)
                    messages.success(request, 'Login successful!')
                    return redirect('user-dashboard')
                else:
                    messages.error(request, 'Invalid or expired OTP.')
            return render(request, 'accounts/otp_login.html', {'form': form})
        else:
            # Step 1: Validate credentials
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            print('DEBUG: is_phone_verified =', user.is_phone_verified)
            if user is not None:
                # Only require OTP if user is not verified
                if not user.is_phone_verified:
                    send_otp_via_email(user)
                    request.session['otp_username'] = user.username
                    form = OTPVerificationForm()
                    return render(request, 'accounts/otp_login.html', {'form': form})
                else:
                    login(request, user)
                    messages.success(request, 'Login successful!')
                    return redirect('user-dashboard')
            else:
                messages.error(request, 'No account found with that username or email. Please register first.')
    return render(request, 'accounts/custom_login.html')

def custom_logout(request):
    logout(request)
    return redirect('home')
