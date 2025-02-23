from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify
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
    watchlist = Profile.watchlist
    print("========")
    print(profile.watchlist)
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

@login_required
def add_to_watchlist(request, item_type, item_id):
    profile = request.user.profile  # Get user's profile

    # Retrieve or initialize the watchlist
    if not profile.watchlist or not isinstance(profile.watchlist, dict):
        watchlist = {"movies": [], "games": [], "books": []}  # Default structure
    else:
        watchlist = profile.watchlist  # Retrieve existing watchlist

    # Ensure the "movies" key exists
    if "movies" not in watchlist:
        watchlist["movies"] = []

    print("++++++++++")  # Debugging: Ensure movies exist
    print(watchlist["movies"])

    # Add the movie if it's not already in the list
    if item_type == "movie":
        original_title = item_id.replace("-", " ").title()  # Convert slug back to readable format
        if original_title not in watchlist["movies"]:  # Avoid duplicates
            watchlist["movies"].append(original_title)

    # Save updated watchlist
    profile.watchlist = watchlist
    profile.save()

    return redirect("accounts:profile")  # Redirect to the profile page


# @login_required
# def remove_from_watchlist(request, movie_title):
#     profile = request.user.profile
#     if movie_title in profile.watchlist_movies:
#         profile.watchlist_movies.remove(movie_title)
#         profile.save()
#     return redirect('profile')