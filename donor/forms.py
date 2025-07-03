from django import forms
from blood.models import CustomUser
from . import models


class DonorUserForm(forms.ModelForm):
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

class DonorForm(forms.ModelForm):
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and (age < 18 or age > 65):
            raise forms.ValidationError('Age must be between 18 and 65.')
        return age
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile and not mobile.isdigit():
            raise forms.ValidationError('Mobile number must contain only digits.')
        return mobile
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_pic'].required = False
        self.fields['address'].widget.attrs['class'] = 'form-control'
        self.fields['address'].widget.attrs['placeholder'] = 'Enter your full address'
        self.fields['city'].widget.attrs['class'] = 'form-control'
        self.fields['city'].widget.attrs['placeholder'] = 'Enter your city'
        self.fields['state'].widget.attrs['class'] = 'form-control'
        self.fields['state'].widget.attrs['placeholder'] = 'Enter your state'
        self.fields['pincode'].widget.attrs['class'] = 'form-control'
        self.fields['pincode'].widget.attrs['placeholder'] = 'Enter your pincode'
        self.fields['mobile'].widget.attrs['class'] = 'form-control'
        self.fields['mobile'].widget.attrs['placeholder'] = 'Enter your mobile number'
        self.fields['bloodgroup'].widget.attrs['class'] = 'form-control'
        self.fields['age'].widget.attrs['class'] = 'form-control'
        self.fields['age'].widget.attrs['placeholder'] = 'Enter your age'
        self.fields['age'].widget.attrs['min'] = '18'
        self.fields['age'].widget.attrs['max'] = '65'
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
        fields=['age','bloodgroup','cause','unit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If initial values are set, make bloodgroup and age read-only (not disabled)
        if self.initial.get('bloodgroup'):
            self.fields['bloodgroup'].widget.attrs['readonly'] = True
        if self.initial.get('age'):
            self.fields['age'].widget.attrs['readonly'] = True
