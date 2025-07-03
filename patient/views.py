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


def patient_signup_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            my_patient_group, created = Group.objects.get_or_create(name='PATIENT')
            user.groups.add(my_patient_group)
            user.is_staff = False
            user.is_superuser = False
            user.save()
            print('Patient registration successful:', user.username)
            return redirect('patientlogin')
        else:
            print('Patient registration failed. UserForm errors:', userForm.errors)
            print('Patient registration failed. PatientForm errors:', patientForm.errors)
            mydict['registration_failed'] = True
    return render(request,'patient/patientsignup.html',context=mydict)

def patient_dashboard_view(request):
    try:
        patient = models.Patient.objects.get(user_id=request.user.id)
        dict = {
            'requestpending': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Pending').count(),
            'requestapproved': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Approved').count(),
            'requestmade': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).count(),
            'requestrejected': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Rejected').count(),
        }
        return render(request, 'patient/patient_dashboard.html', context=dict)
    except models.Patient.DoesNotExist:
        # If patient profile doesn't exist, redirect to signup
        return redirect('patient-signup')

def make_request_view(request):
    try:
        patient = models.Patient.objects.get(user_id=request.user.id)
        # Pre-fill initial data from patient profile
        initial_data = {
            'patient_name': patient.user.first_name + ' ' + patient.user.last_name,
            'patient_age': patient.age,
            'bloodgroup': patient.bloodgroup,
        }
        request_form = bforms.RequestForm(initial=initial_data)
        # Make fields readonly in the template by passing a flag
        readonly_fields = ['patient_name', 'patient_age', 'bloodgroup']
        if request.method == 'POST':
            request_form = bforms.RequestForm(request.POST)
            if request_form.is_valid():
                blood_request = request_form.save(commit=False)
                # Overwrite with patient info to ensure integrity
                blood_request.patient_name = patient.user.first_name + ' ' + patient.user.last_name
                blood_request.patient_age = patient.age
                blood_request.bloodgroup = patient.bloodgroup
                blood_request.request_by_patient = patient
                blood_request.save()
                return HttpResponseRedirect('my-request')
        return render(request, 'patient/makerequest.html', {'request_form': request_form, 'readonly_fields': readonly_fields})
    except models.Patient.DoesNotExist:
        return redirect('patient-signup')

def my_request_view(request):
    try:
        patient = models.Patient.objects.get(user_id=request.user.id)
        blood_request = bmodels.BloodRequest.objects.all().filter(request_by_patient=patient)
        return render(request, 'patient/my_request.html', {'blood_request': blood_request})
    except models.Patient.DoesNotExist:
        return redirect('patient-signup')
