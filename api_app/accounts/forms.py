from django import forms
from.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm

class CustomUserCreationForm(UserCreationForm):
    bio = forms.CharField(widget=forms.Textarea, required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('username', 'bio', 'profile_picture')

class ProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)  # Add username field

    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio']  # Add any fields from Profile model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].initial = self.instance.user.username  # Pre-fill username

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.username = self.cleaned_data['username']  # Update User model

        if commit:
            profile.user.save()
            profile.save()
        return profile
