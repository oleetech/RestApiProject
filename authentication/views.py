# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse
from .forms import UserProfileForm

CustomUser = get_user_model()

@login_required
def update_profile(request):
    user = request.user  # Get the currently logged-in user

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)

        # Only allow company to be set if it hasn't been set before
        if form.is_valid():
            # Prevent changing the company after it's been set
            if user.company and 'company' in form.changed_data:
                messages.error(request, 'You cannot change your company after it has been set.')
            else:
                form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect(reverse('update_profile'))  # Redirect to the same page after successful update
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserProfileForm(instance=user)  # Pre-fill the form with current user data

    context = {
        'form': form,
    }
    return render(request, 'update_profile.html', context)
