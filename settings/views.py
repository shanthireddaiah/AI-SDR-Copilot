from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserProfile
from .forms import UserProfileForm

@login_required
def settings_index_view(request):
    """
    Renders and updates User Profile, API Configuration, and Security settings.
    """
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile':
            profile_form = UserProfileForm(request.POST, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                
                # Update User model fields
                request.user.first_name = profile_form.cleaned_data.get('first_name', '')
                request.user.last_name = profile_form.cleaned_data.get('last_name', '')
                request.user.email = profile_form.cleaned_data.get('email', '')
                request.user.save()

                messages.success(request, "Your profile and API settings were updated successfully!")
                return redirect('settings:index')
            else:
                messages.error(request, "Please correct the errors in your profile form.")
                password_form = PasswordChangeForm(user=request.user)
        
        elif form_type == 'password':
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password was changed successfully!")
                return redirect('settings:index')
            else:
                messages.error(request, "Failed to change password. Please check requirement criteria.")
                profile_form = UserProfileForm(instance=profile)
    else:
        profile_form = UserProfileForm(instance=profile)
        password_form = PasswordChangeForm(user=request.user)

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'profile': profile
    }
    return render(request, 'settings/index.html', context)
