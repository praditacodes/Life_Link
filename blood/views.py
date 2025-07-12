from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta, datetime
from django.core.mail import send_mail
from django.contrib.auth.models import User
from donor import models as dmodels
from patient import models as pmodels
from donor import forms as dforms
from patient import forms as pforms
from django.contrib.auth import logout, login, authenticate, update_session_auth_hash
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from django.contrib import messages
from .utils import generate_otp, send_otp_via_email, is_otp_valid
from .forms import OTPVerificationForm, EmailForm, PasswordResetForm, ChangePasswordForm
from .models import CustomUser
from phonenumber_field.phonenumber import to_python
from django.db.models import Count, Max
from django.db.models.functions import TruncMonth
import json
from accounts.models import Profile


def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('home')

def home_view(request):
    x = models.Stock.objects.all()
    print(x)
    if len(x) == 0:
        blood1 = models.Stock()
        blood1.bloodgroup = "A+"
        blood1.save()
        blood2 = models.Stock()
        blood2.bloodgroup = "A-"
        blood2.save()
        blood3 = models.Stock()
        blood3.bloodgroup = "B+"
        blood3.save()
        blood4 = models.Stock()
        blood4.bloodgroup = "B-"
        blood4.save()
        blood5 = models.Stock()
        blood5.bloodgroup = "AB+"
        blood5.save()
        blood6 = models.Stock()
        blood6.bloodgroup = "AB-"
        blood6.save()
        blood7 = models.Stock()
        blood7.bloodgroup = "O+"
        blood7.save()
        blood8 = models.Stock()
        blood8.bloodgroup = "O-"
        blood8.save()
    # Always show landing page, even for logged-in users
    return render(request, 'blood/index.html')

def is_donor(user):
    return user.groups.filter(name='DONOR').exists()

def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


def afterlogin_view(request):
    return redirect('user-dashboard')

@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    totalunit = models.Stock.objects.aggregate(Sum('unit'))
    # Key stats
    total_donations = dmodels.BloodDonate.objects.filter(status='Approved').count()
    total_units_donated = dmodels.BloodDonate.objects.filter(status='Approved').aggregate(Sum('unit'))['unit__sum'] or 0
    # Top donors (by total units donated)
    top_donors = (
        dmodels.BloodDonate.objects.filter(status='Approved')
        .values('donor__user__first_name', 'donor__user__last_name', 'donor__blood_group')
        .annotate(total_units=Sum('unit'), donation_count=Count('id'), last_donation=Max('date'))
        .order_by('-total_units')[:5]
    )
    # Donations per month (for chart)
    donations_per_month = (
        dmodels.BloodDonate.objects.filter(status='Approved')
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('unit'))
        .order_by('month')
    )
    chart_labels = [d['month'].strftime('%b %Y') for d in donations_per_month]
    chart_data = [d['total'] for d in donations_per_month]
    # Blood group distribution (for chart)
    bloodgroup_dist = (
        dmodels.BloodDonate.objects.filter(status='Approved')
        .values('bloodgroup')
        .annotate(total=Sum('unit'))
        .order_by('-total')
    )
    bg_labels = [d['bloodgroup'] for d in bloodgroup_dist]
    bg_data = [d['total'] for d in bloodgroup_dist]
    dict = {
        'A1': models.Stock.objects.get_or_create(bloodgroup="A+")[0],
        'A2': models.Stock.objects.get_or_create(bloodgroup="A-")[0],
        'B1': models.Stock.objects.get_or_create(bloodgroup="B+")[0],
        'B2': models.Stock.objects.get_or_create(bloodgroup="B-")[0],
        'AB1': models.Stock.objects.get_or_create(bloodgroup="AB+")[0],
        'AB2': models.Stock.objects.get_or_create(bloodgroup="AB-")[0],
        'O1': models.Stock.objects.get_or_create(bloodgroup="O+")[0],
        'O2': models.Stock.objects.get_or_create(bloodgroup="O-")[0],
        'totaldonors': dmodels.Donor.objects.all().count(),
        'totalbloodunit': totalunit['unit__sum'],
        'totalrequest': models.BloodRequest.objects.all().count(),
        'totalapprovedrequest': models.BloodRequest.objects.all().filter(status='Approved').count(),
        'total_donations': total_donations,
        'total_units_donated': total_units_donated,
        'top_donors': top_donors,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'bg_labels': json.dumps(bg_labels),
        'bg_data': json.dumps(bg_data),
    }
    return render(request, 'blood/admin_dashboard.html', context=dict)

@login_required(login_url='adminlogin')
def admin_blood_view(request):
    dict={
        'bloodForm':forms.BloodForm(),
        'A1':models.Stock.objects.get_or_create(bloodgroup="A+")[0],
        'A2':models.Stock.objects.get_or_create(bloodgroup="A-")[0],
        'B1':models.Stock.objects.get_or_create(bloodgroup="B+")[0],
        'B2':models.Stock.objects.get_or_create(bloodgroup="B-")[0],
        'AB1':models.Stock.objects.get_or_create(bloodgroup="AB+")[0],
        'AB2':models.Stock.objects.get_or_create(bloodgroup="AB-")[0],
        'O1':models.Stock.objects.get_or_create(bloodgroup="O+")[0],
        'O2':models.Stock.objects.get_or_create(bloodgroup="O-")[0],
    }
    if request.method=='POST':
        bloodForm=forms.BloodForm(request.POST)
        if bloodForm.is_valid() :        
            bloodgroup=bloodForm.cleaned_data['bloodgroup']
            stock=models.Stock.objects.get(bloodgroup=bloodgroup)
            stock.unit=bloodForm.cleaned_data['unit']
            stock.save()
        return HttpResponseRedirect('admin-blood')
    return render(request,'blood/admin_blood.html',context=dict)


@login_required(login_url='adminlogin')
def admin_donor_view(request):
    from accounts.models import Profile
    donors = Profile.objects.filter(can_donate=True)
    return render(request, 'blood/admin_donor.html', {'donors': donors})

@login_required(login_url='adminlogin')
def update_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=CustomUser.objects.get(id=donor.user_id)
    userForm=dforms.DonorUserForm(instance=user)
    donorForm=dforms.DonorForm(request.FILES,instance=donor)
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=dforms.DonorUserForm(request.POST,instance=user)
        donorForm=dforms.DonorForm(request.POST,request.FILES,instance=donor)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            return redirect('admin-donor')
    return render(request,'blood/update_donor.html',context=mydict)


@login_required(login_url='adminlogin')
def delete_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=CustomUser.objects.get(id=donor.user_id)
    donor.delete()
    user.delete()
    return redirect('admin-donor')

@login_required(login_url='adminlogin')
def admin_patient_view(request):
    from accounts.models import Profile
    patients = Profile.objects.filter(can_receive=True)
    return render(request, 'blood/admin_patient.html', {'patients': patients})


@login_required(login_url='adminlogin')
def update_patient_view(request,pk):
    patient=pmodels.Patient.objects.get(id=pk)
    user=pmodels.User.objects.get(id=patient.user_id)
    userForm=pforms.PatientUserForm(instance=user)
    patientForm=pforms.PatientForm(request.FILES,instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=pforms.PatientUserForm(request.POST,instance=user)
        patientForm=pforms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            return redirect('admin-patient')
    return render(request,'blood/update_patient.html',context=mydict)


@login_required(login_url='adminlogin')
def delete_patient_view(request,pk):
    patient=pmodels.Patient.objects.get(id=pk)
    user=CustomUser.objects.get(id=patient.user_id)
    patient.delete()
    user.delete()
    return redirect('admin-patient')

@login_required(login_url='adminlogin')
def admin_request_view(request):
    requests=models.BloodRequest.objects.all().filter(status='Pending')
    return render(request,'blood/admin_request.html',{'requests':requests})

@login_required(login_url='adminlogin')
def admin_request_history_view(request):
    requests=models.BloodRequest.objects.all().exclude(status='Pending')
    return render(request,'blood/admin_request_history.html',{'requests':requests})

@login_required(login_url='adminlogin')
def admin_donation_view(request):
    donations=dmodels.BloodDonate.objects.all()
    return render(request,'blood/admin_donation.html',{'donations':donations})

@login_required(login_url='adminlogin')
def update_approve_status_view(request,pk):
    req=models.BloodRequest.objects.get(id=pk)
    message=None
    bloodgroup=req.blood_group
    unit=req.unit
    stock=models.Stock.objects.get(bloodgroup=bloodgroup)
    if stock.unit > unit:
        stock.unit=stock.unit-unit
        stock.save()
        req.status="Approved"
        
    else:
        message="Stock Doest Not Have Enough Blood To Approve This Request, Only "+str(stock.unit)+" Unit Available"
    req.save()

    requests=models.BloodRequest.objects.all().filter(status='Pending')
    return render(request,'blood/admin_request.html',{'requests':requests,'message':message})

@login_required(login_url='adminlogin')
def update_reject_status_view(request,pk):
    req=models.BloodRequest.objects.get(id=pk)
    req.status="Rejected"
    req.save()
    return HttpResponseRedirect('/admin-request')

@login_required(login_url='adminlogin')
def approve_donation_view(request,pk):
    donation=dmodels.BloodDonate.objects.get(id=pk)
    donation_blood_group=donation.bloodgroup
    donation_blood_unit=donation.unit

    # Ensure stock entry exists for this blood group
    stock, created = models.Stock.objects.get_or_create(bloodgroup=donation_blood_group, defaults={'unit': 0})
    stock.unit=stock.unit+donation_blood_unit
    stock.save()

    donation.status='Approved'
    donation.save()
    return HttpResponseRedirect('/admin-donation')


@login_required(login_url='adminlogin')
def reject_donation_view(request,pk):
    donation=dmodels.BloodDonate.objects.get(id=pk)
    donation.status='Rejected'
    donation.save()
    return HttpResponseRedirect('/admin-donation')

@login_required
@user_passes_test(lambda u: u.is_authenticated)
def search_donors_view(request):
    from geopy.geocoders import Nominatim
    from geopy.distance import geodesic
    from django.db.models import Q
    donors = []
    search_coords = None
    show_all = False
    donor_markers = []
    if request.method == 'GET':
        bloodgroup = request.GET.get('bloodgroup')
        city = request.GET.get('city')
        radius = request.GET.get('radius', 10)
        if bloodgroup:
            all_donors = Profile.objects.filter(blood_group=bloodgroup, can_donate=True)
            local_donors = []
            far_donors = []
            donor_set = set()
            if city:
                geolocator = Nominatim(user_agent="blood_link")
                try:
                    location = geolocator.geocode(city)
                    if location:
                        search_coords = (location.latitude, location.longitude)
                        for donor in all_donors:
                            if donor.latitude and donor.longitude:
                                donor_coords = (float(donor.latitude), float(donor.longitude))
                                distance = geodesic(search_coords, donor_coords).kilometers
                                donor.distance = distance
                                if distance <= float(radius):
                                    local_donors.append(donor)
                                    donor_set.add(donor.pk)
                                else:
                                    far_donors.append(donor)
                            else:
                                far_donors.append(donor)
                except Exception as e:
                    print(f"Error in geocoding: {e}")
            else:
                far_donors = list(all_donors)
            # If no local donors, show all
            if not local_donors:
                show_all = True
                donors = far_donors
            else:
                donors = local_donors + [d for d in far_donors if d.pk not in donor_set]
            # Sort by distance if available, else by city
            donors.sort(key=lambda x: (getattr(x, 'distance', None) if hasattr(x, 'distance') and x.distance is not None else 99999, x.city or ''))
            # Prepare donor_markers for map
            for donor in donors:
                if donor.latitude and donor.longitude:
                    donor_markers.append({
                        'lat': float(donor.latitude),
                        'lng': float(donor.longitude),
                        'name': f"{donor.user.first_name} {donor.user.last_name}",
                        'city': donor.city or ''
                    })
    return render(request, 'blood/search.html', {
        'donors': donors,
        'search_coords': search_coords,
        'show_all': show_all,
        'donor_markers': json.dumps(donor_markers)
    })

def verify_email(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = request.user
            user.email = email
            user.save()
            
            # Generate and send OTP
            otp = generate_otp()
            if send_otp_via_email(email, otp):
                user.otp = otp
                user.otp_created_at = datetime.now()
                user.save()
                return redirect('verify_otp')
            else:
                messages.error(request, 'Failed to send OTP. Please try again.')
    else:
        form = EmailForm()
    return render(request, 'blood/verify_email.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            user = request.user
            
            if user.otp == otp and is_otp_valid(user.otp_created_at):
                user.is_phone_verified = True  # We'll keep this field name for compatibility
                user.otp = None
                user.otp_created_at = None
                user.save()
                messages.success(request, 'Email verified successfully!')
                return redirect('afterlogin')
            else:
                messages.error(request, 'Invalid or expired OTP')
    else:
        form = OTPVerificationForm()
    return render(request, 'blood/verify_otp.html', {'form': form})

def forgot_password(request):
    """
    Step 1: User enters email. If valid, send OTP and redirect to OTP entry.
    """
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                otp = generate_otp()
                # Send OTP via email
                result = send_otp_via_email(email, otp)
                if result is True:
                    user.otp = otp
                    user.otp_created_at = datetime.now()
                    user.save()
                    request.session['reset_email'] = email
                    return redirect('reset_password_otp')
                else:
                    messages.error(request, f'Failed to send OTP. {result if isinstance(result, str) else "Please try again."}')
            except CustomUser.DoesNotExist:
                messages.error(request, 'No user found with this email address.')
    else:
        form = EmailForm()
    return render(request, 'blood/forgot_password.html', {'form': form})

def reset_password_otp(request):
    """
    Step 2: User enters OTP. If valid, redirect to password reset form.
    """
    if 'reset_email' not in request.session:
        return redirect('forgot_password')
        
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            email = request.session['reset_email']
            try:
                user = CustomUser.objects.get(email=email)
                if user.otp == otp and is_otp_valid(user.otp_created_at):
                    user.otp = None
                    user.otp_created_at = None
                    user.save()
                    return redirect('reset_password')
                else:
                    messages.error(request, 'Invalid or expired OTP')
            except CustomUser.DoesNotExist:
                messages.error(request, 'User not found')
    else:
        form = OTPVerificationForm()
    return render(request, 'blood/reset_password_otp.html', {'form': form})

def reset_password(request):
    """
    Step 3: User sets a new password. If successful, redirect to login.
    """
    if 'reset_email' not in request.session:
        return redirect('forgot_password')
        
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = request.session['reset_email']
            try:
                user = CustomUser.objects.get(email=email)
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                del request.session['reset_email']
                messages.success(request, 'Password reset successful! Please login with your new password.')
                return redirect('patientlogin')
            except CustomUser.DoesNotExist:
                messages.error(request, 'User not found')
    else:
        form = PasswordResetForm()
    return render(request, 'blood/reset_password.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            if user.check_password(form.cleaned_data['current_password']):
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully!')
                return redirect('afterlogin')
            else:
                messages.error(request, 'Current password is incorrect')
    else:
        form = ChangePasswordForm()
    return render(request, 'blood/change_password.html', {'form': form})