from django import forms
from blood.models import CustomUser
from . import models


class PatientUserForm(forms.ModelForm):
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
        # self.fields['pincode'].required = False  # Not included in form fields below

    class Meta:
        model=models.Patient
        fields=['age','bloodgroup','disease','address','doctorname','mobile','profile_pic','city','state']
