from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from.forms import CustomUserCreationForm
from.models import Profile

class RegisterView(CreateView):
    form_class = CustomUserCreationForm  # Use the custom form
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"
    
@login_required
def profile_view(request):
    profile = request.user.profile  # Access the user's profile
    return render(request, 'profile/profile.html', {'profile': profile})

@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return render(request, 'profile/profile.html', {'profile': profile})
    else:
        form = CustomUserCreationForm(instance=profile)  # Pass the instance here
    return render(request, 'profile/editProfile.html', {'form': form})

# @login_required
# def add_watched_movie(request, imdb_id):
#     watched, created = WatchedMovie.objects.get_or_create(user=request.user, imdb_id=imdb_id)
    
#     if created:
#         return JsonResponse({'message': 'Movie added to watched list!'})
#     return JsonResponse({'message': 'Movie already in watched list!'})