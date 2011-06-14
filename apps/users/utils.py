from django.contrib import auth

from users.forms import AuthenticationForm, RegistrationForm
from users.models import Profile


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


def get_next_url(request):
    """Given a request object, return a safe next URL."""
    gets = request.GET.copy()
    if auth.REDIRECT_FIELD_NAME not in gets:
        return None
    url = gets[auth.REDIRECT_FIELD_NAME]
    if url and '://' in url:
        url = None
    return url
