from django import forms
from.models import Profile
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    bio = forms.CharField(widget=forms.Textarea, required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('username', 'bio', 'profile_picture')