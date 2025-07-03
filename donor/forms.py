from django import forms
from blood.models import CustomUser
from . import models


class DonorUserForm(forms.ModelForm):
    class Meta:
        model=CustomUser
        fields=['first_name','last_name','username','email','password']
        widgets = {
        'password': forms.PasswordInput()
        }

class DonorForm(forms.ModelForm):
    class Meta:
        model=models.Donor
        fields=['bloodgroup','age','address','mobile','profile_pic','city','state','pincode']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your city'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your state'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your pincode'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your mobile number'}),
            'bloodgroup': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your age', 'min': 18, 'max': 65}),
        }

class DonationForm(forms.ModelForm):
    class Meta:
        model=models.BloodDonate
        fields=['age','bloodgroup','disease','unit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If initial values are set, make bloodgroup and age read-only (not disabled)
        if self.initial.get('bloodgroup'):
            self.fields['bloodgroup'].widget.attrs['readonly'] = True
        if self.initial.get('age'):
            self.fields['age'].widget.attrs['readonly'] = True
