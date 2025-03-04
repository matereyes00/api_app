from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    username = forms.CharField(max_length=150, required=True, label='Username') #added labels
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Password') #added labels
    bio = forms.Textarea()
    profile_picture = forms.ImageField()
    
    
    class Meta:
        model = User
        fields = ["username", "password", "email", "profile_picture"]
        
class LoginForm(forms.Form):  # Inherit from forms.Form
    username = forms.CharField(max_length=150, required=True, label='Username') #added labels
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Password') #added labels