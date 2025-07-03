from django import forms
from blood.models import CustomUser
from . import models


class PatientUserForm(forms.ModelForm):
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or '@' not in email:
            raise forms.ValidationError('Enter a valid email address.')
        return email
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('first_name') or not cleaned_data.get('last_name'):
            raise forms.ValidationError('First and last name are required.')
        return cleaned_data
    class Meta:
        model=CustomUser
        fields=['first_name','last_name','username','email','password']
        widgets = {
        'password': forms.PasswordInput()
        }

class PatientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].required = True
        self.fields['state'].required = True
        self.fields['profile_pic'].required = False
        # self.fields['pincode'].required = False  # Not included in form fields below

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and (age < 0 or age > 120):
            raise forms.ValidationError('Enter a valid age.')
        return age
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile and not mobile.isdigit():
            raise forms.ValidationError('Mobile number must contain only digits.')
        return mobile
    class Meta:
        model=models.Patient
        fields=['age','bloodgroup','cause','address','doctorname','mobile','profile_pic','city','state']
