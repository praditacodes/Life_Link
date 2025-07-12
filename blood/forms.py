from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from phonenumber_field.formfields import PhoneNumberField

from . import models


class BloodForm(forms.ModelForm):
    class Meta:
        model=models.Stock
        fields=['bloodgroup','unit']

class RequestForm(forms.ModelForm):
    class Meta:
        model=models.BloodRequest
        fields=['patient_name','patient_age','reason','blood_group','unit']

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, min_length=6, widget=forms.TextInput(attrs={'class': 'input--style-5'}))

class EmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'input--style-5'}),
        help_text="Enter your email address"
    )

class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input--style-5'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input--style-5'}))

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data

class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input--style-5'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input--style-5'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input--style-5'}))

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email")
