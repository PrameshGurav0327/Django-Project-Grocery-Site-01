from django import forms
from .models import Address
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'pincode', 'city', 'state', 'street_address', 'landmark']


class SignupForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(label="First Name", required=False)
    last_name = forms.CharField(label="Last Name", required=False)
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
