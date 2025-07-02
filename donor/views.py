from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from blood import forms as bforms
from blood import models as bmodels
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from patient.models import Patient
from blood.models import CustomUser
from geopy.distance import geodesic
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse

def donor_signup_view(request):
    userForm=forms.DonorUserForm()
    donorForm=forms.DonorForm()
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=forms.DonorUserForm(request.POST)
        donorForm=forms.DonorForm(request.POST,request.FILES)
        if userForm.is_valid() and donorForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            
            # Get location coordinates
            try:
                geolocator = Nominatim(user_agent="blood_link")
                location_str = f"{donor.address}, {donor.city}, {donor.state}, {donor.pincode}"
                location = geolocator.geocode(location_str, timeout=10)
                if location:
                    donor.latitude = location.latitude
                    donor.longitude = location.longitude
            except Exception as e:
                # Log the error or pass, but do not block registration
                pass
            
            donor.save()
            my_donor_group, created = Group.objects.get_or_create(name='DONOR')
            user.groups.add(my_donor_group)
            user.is_staff = False
            user.is_superuser = False
            user.save()
        return HttpResponseRedirect('donorlogin')
    return render(request,'donor/donorsignup.html',context=mydict)


def donor_dashboard_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    dict={
        'requestpending': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Pending').count(),
        'requestapproved': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Approved').count(),
        'requestmade': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).count(),
        'requestrejected': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Rejected').count(),
    }
    return render(request,'donor/donor_dashboard.html',context=dict)


def donate_blood_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    initial_data = {
        'bloodgroup': donor.bloodgroup,
        'age': getattr(donor, 'age', ''),
    }
    donation_form = forms.DonationForm(initial=initial_data)
    if request.method == 'POST':
        donation_form = forms.DonationForm(request.POST)
        if donation_form.is_valid():
            blood_donate = donation_form.save(commit=False)
            blood_donate.bloodgroup = donor.bloodgroup
            blood_donate.age = getattr(donor, 'age', '')
            blood_donate.donor = donor
            blood_donate.save()
            return HttpResponseRedirect('donation-history')  
    return render(request, 'donor/donate_blood.html', {'donation_form': donation_form})

def donation_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    donations=models.BloodDonate.objects.all().filter(donor=donor)
    return render(request,'donor/donation_history.html',{'donations':donations})

def register_patient(request):
    # ... get data from form ...
    user = CustomUser.objects.create_user(username=username, email=email, password=password, phone_number=phone_number)
    patient = Patient.objects.create(
        user=user,
        # ... other fields ...
    )

def search_donors_view(request):
    donors = []
    if request.method == 'GET':
        bloodgroup = request.GET.get('bloodgroup')
        city = request.GET.get('city')
        radius = request.GET.get('radius', 10)  # Default 10km radius

        if bloodgroup and city:
            geolocator = Nominatim(user_agent="blood_link")
            location = geolocator.geocode(city)
            if location:
                search_coords = (location.latitude, location.longitude)
                donor_list = models.Donor.objects.filter(bloodgroup=bloodgroup)
                for donor in donor_list:
                    if donor.latitude and donor.longitude:
                        donor_coords = (float(donor.latitude), float(donor.longitude))
                        distance = geodesic(search_coords, donor_coords).kilometers
                        if distance <= float(radius):
                            donor.distance = distance
                            donors.append(donor)
                donors.sort(key=lambda x: x.distance)
    return render(request, 'blood/search.html', {'donors': donors})

@login_required
def download_certificate(request, donation_id):
    from django.shortcuts import get_object_or_404
    donation = get_object_or_404(models.BloodDonate, id=donation_id, donor__user=request.user, status='Approved')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="donation_certificate_{donation.id}.pdf"'
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    # Certificate design
    p.setFont("Helvetica-Bold", 24)
    p.setFillColorRGB(0.85, 0.1, 0.1)
    p.drawCentredString(width/2, height-100, "Blood Donation Certificate")
    p.setFont("Helvetica", 14)
    p.setFillColorRGB(0,0,0)
    p.drawCentredString(width/2, height-140, f"This is to certify that")
    p.setFont("Helvetica-Bold", 18)
    donor_name = f"{donation.donor.user.first_name} {donation.donor.user.last_name}"
    p.drawCentredString(width/2, height-180, donor_name)
    p.setFont("Helvetica", 14)
    p.drawCentredString(width/2, height-210, f"has donated {donation.unit} ml of {donation.bloodgroup} blood on {donation.date}")
    p.drawCentredString(width/2, height-240, "Thank you for your life-saving contribution!")
    p.setFont("Helvetica-Oblique", 12)
    p.drawCentredString(width/2, height-280, "- Life-Link Blood Bank")
    p.showPage()
    p.save()
    return response
