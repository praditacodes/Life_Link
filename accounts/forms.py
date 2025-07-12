from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'profile_pic', 'age', 'blood_group', 'address', 'city', 'state', 'pincode',
            'phone', 'can_donate', 'can_receive', 'cause', 'latitude', 'longitude'
        ]
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your city'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your state'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your pincode'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your age', 'min': 0, 'max': 120}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'cause': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason (if requesting blood)'}),
        }

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, label='Enter OTP', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the OTP sent to your email'})) 