from django import forms
from .models import Profile
from django.core.exceptions import ValidationError

def validate_nepal_phone(value):
    if value and not str(value).startswith('+977'):
        raise ValidationError('Phone number must start with +977 (Nepal country code).')

class ProfileForm(forms.ModelForm):
    phone = forms.CharField(
        required=False,
        validators=[validate_nepal_phone],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number (+977XXXXXXXXXX)',
            'maxlength': '15',
        }),
        help_text='Phone number must start with +977 (Nepal country code).',
    )
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
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your age', 'min': 0, 'max': 120}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'cause': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason (if requesting blood)'}),
        }

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, label='Enter OTP', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the OTP sent to your email'})) 