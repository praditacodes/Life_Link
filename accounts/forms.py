from django import forms
from .models import Profile
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
import re

User = get_user_model()

def validate_nepal_phone(value):
    if value and not str(value).startswith('+977'):
        raise ValidationError('Phone number must start with +977 (Nepal country code).')

class ProfileForm(forms.ModelForm):
    phone = forms.CharField(
        required=True,
        validators=[validate_nepal_phone],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number (+977XXXXXXXXXX)',
            'maxlength': '15',
        }),
        help_text='Phone number must start with +977 (Nepal country code).',
    )
    age = forms.IntegerField(
        required=True,
        min_value=0,
        max_value=120,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your age', 'min': 0, 'max': 120}),
        help_text='Enter your age.'
    )
    blood_group = forms.ChoiceField(
        required=True,
        choices=[('', 'Select blood group')] + list(Profile._meta.get_field('blood_group').choices),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Select your blood group.'
    )
    address = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full address'}),
    )
    city = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your city'}),
    )
    state = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your state'}),
    )
    pincode = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your pincode'}),
    )
    can_donate = forms.BooleanField(required=False)
    can_receive = forms.BooleanField(required=False)
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
    def clean(self):
        cleaned_data = super().clean()
        age = cleaned_data.get('age')
        can_donate = cleaned_data.get('can_donate')
        if age is not None and (age < 0 or age > 120):
            self.add_error('age', 'Age must be between 0 and 120.')
        # Additional donor age validation
        if can_donate and age is not None and age < 18:
            self.add_error('age', 'You must be at least 18 years old to register as a donor.')
        return cleaned_data

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, label='Enter OTP', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the OTP sent to your email'}))

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '')
        if not first_name.isalpha():
            raise forms.ValidationError('First name must contain only letters.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '')
        if not last_name.isalpha():
            raise forms.ValidationError('Last name must contain only letters.')
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError('Email must end with @gmail.com.')
        # Allowed: letters, digits, dots, underscores, no spaces or other special chars
        local_part = email.split('@')[0]
        if not re.match(r'^[A-Za-z0-9][A-Za-z0-9._]*$', local_part):
            raise forms.ValidationError('Email must start with a letter or digit and only contain letters, digits, dots, or underscores before @gmail.com.')
        if ' ' in email:
            raise forms.ValidationError('Email must not contain spaces.')
        return email 