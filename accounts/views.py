from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render



class RegisterView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"
    
@login_required(login_url='accounts/login/')
def profile_view(request):
    profile = request.user.profile  # Access the user's profile
    return render(request, 'profile/profile.html', {'profile': profile})

@login_required(login_url='accounts/login/')
def edit_profile_view(request):
    return render(request, 'profile/edit_profile.html')