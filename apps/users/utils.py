from django.conf import settings
from django.contrib import auth
from django.http import Http404
from django.utils.http import base36_to_int

from users.forms import (AuthenticationForm, RegistrationForm, SetPasswordForm,
                         ProfileForm)
from users.models import Profile, User


def handle_signin(request):
    """Helper function that signs a user in."""
    auth.logout(request)
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth.login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
        return form
    request.session.set_test_cookie()
    return AuthenticationForm()


def handle_signup(request):
    """Helper function for signups."""
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            profile = Profile.objects.create_profile(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email'],
            )
            profile.send_confirmation_email()
        return form
    return RegistrationForm()


def handle_password_reset(request):
    """Helper function for password resets."""
    if request.method == 'POST':
        form = auth.forms.PasswordResetForm(data=request.POST)
        if form.is_valid():
            form.save(use_https=request.is_secure(),
                      token_generator=auth.tokens.default_token_generator,
                      from_email=settings.DEFAULT_FROM_EMAIL,
                      email_template_name='users/email/password_reset.txt')
        return form
    return auth.forms.PasswordResetForm()


def handle_password_reset_confirm(request, uidb36, token):
    """Present set password form or perform actual password reset."""
    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(id=uid_int)
    except (ValueError, User.DoesNotExist):
        raise Http404

    if not auth.tokens.default_token_generator.check_token(user, token):
        raise Http404

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
        return form
    return SetPasswordForm(None)


def handle_profile_save(request):
    """Edit or create a user profile."""
    profile = request.user.get_profile()
    if request.method == 'POST':
        form = ProfileForm(data=request.POST,
                           files=request.FILES,
                           instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
        return form
    return ProfileForm(instance=profile)


def get_next_url(request):
    """Given a request object, return a safe next URL."""
    gets = request.GET.copy()
    if auth.REDIRECT_FIELD_NAME not in gets:
        return None
    url = gets[auth.REDIRECT_FIELD_NAME]
    if url and '://' in url:
        url = None
    return url
