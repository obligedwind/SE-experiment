from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django import forms
from django.core.validators import RegexValidator

class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    phone_regex = RegexValidator(regex=r'^1\d{10}$',
                                 message="Phone number must be entered in the format: '1XXXXXXXXXX'. Up to 11 digits allowed.")
    phone_number = forms.CharField(
        validators=[phone_regex],
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={'type': 'tel', 'placeholder': 'Enter your phone number'}),
    )


    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
