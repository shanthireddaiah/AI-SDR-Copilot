import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import UserRegisterForm

logger = logging.getLogger('accounts')

def register_view(request):
    """
    Handles user registration.
    If POST request is valid, creates a new user via UserCreationForm (create_user),
    logs them in, and redirects to dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f"[REGISTER SUCCESS] Created user ID={user.id}, username='{user.username}', email='{user.email}' in database.")
            login(request, user)
            messages.success(request, f"Welcome to AI SDR Copilot, {user.username}! Your account was created successfully.")
            return redirect('dashboard:index')
        else:
            logger.warning(f"[REGISTER FAIL] Form errors: {form.errors.as_json()}")
            for error_list in form.errors.values():
                for error in error_list:
                    messages.error(request, error)
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handles user login supporting both username and email address.
    Authenticates credentials and establishes user session with diagnostic debug logging.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        login_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        logger.debug(f"[LOGIN ATTEMPT] Identifier: '{login_input}'")

        # Diagnostics: Check whether user exists in database by username or email
        user_matches = User.objects.filter(
            Q(username__iexact=login_input) | Q(email__iexact=login_input)
        )
        if not user_matches.exists():
            logger.warning(f"[LOGIN FAIL] No user matching username/email '{login_input}' exists in database.")
        else:
            target_user = user_matches.first()
            pwd_ok = target_user.check_password(password)
            logger.debug(f"[LOGIN DIAGNOSTIC] User found: '{target_user.username}', active={target_user.is_active}, pwd_match={pwd_ok}")

        # Authenticate via custom backend (supports username or email)
        user = authenticate(request, username=login_input, password=password)

        if user is not None:
            login(request, user)
            logger.info(f"[LOGIN SUCCESS] Session established for user '{user.username}'.")
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'dashboard:index')
        else:
            logger.warning(f"[LOGIN FAIL] Invalid credentials for identifier '{login_input}'.")
            messages.error(request, "Invalid username or password.")
            form = AuthenticationForm()
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    Handles user logout and terminates active session.
    """
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """
    Redirects user profile request to Settings page.
    """
    return redirect('settings:index')
