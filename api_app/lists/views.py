from django.shortcuts import render

from .forms import CustomListForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# Create your views here.
@login_required
def create_custom_watchlist(request):
    if request.method == 'POST':
        custom_list_form = CustomListForm(request.POST)
        if custom_list_form.is_valid():
            custom_watchlist = custom_list_form.save(commit=False) # create but dont save
            custom_watchlist.user = request.user # assign user before saving
            custom_watchlist.save()
            return redirect('api_app.accounts:profile')  # Redirect after form submission
    else:
        custom_list_form = CustomListForm()
        
    template = 'customWatchlist/addCustomWatchlistForm.html'
    context = {
        'custom_watchlist_form': custom_list_form,
    }

    return render(request, template, context)

def add_to_custom_watchlist(request, category, itemid):
    if request.method == 'POST':
        pass