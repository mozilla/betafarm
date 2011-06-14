from django.conf import settings
from django.contrib.auth.models import User

from users.models import Profile
from users.forms import RegistrationForm

default_form_params = {
    'username': 'username',
    'email': 'username@mozilla.com',
    'password': 'password123',
    'password_confirm': 'password123',
}
_submit_form = lambda d: RegistrationForm(
    dict(default_form_params.items() + d.items()))


def test_user_creation_is_inactive():
    """Test that new users are inactive by default."""
    profile = Profile.objects.create_profile(
        'username', 'username@mozilla.com', 'password123')
    assert isinstance(profile, Profile)
    assert isinstance(profile.user, User)
    assert not profile.user.is_active


def test_user_creation_bad_passwords():
    """Test that new users cannot choose simple passwords."""
    bad_passwords = ('short12', 'allalpha', '1234567890')
    for password in bad_passwords:
        form = _submit_form(dict(password=password, password_confirm=password))
        assert not form.is_valid()
        assert form.errors['__all__'][0].startswith(
            u'Password must be at least 8 characters long')


def test_user_creation_blacklisted_passwords():
    """Test that new users cannot choose blacklisted passwords."""
    blacklisted = getattr(settings, 'PASSWORD_BLACKLIST', None)
    for password in blacklisted:
        form = _submit_form(dict(password=password, password_confirm=password))
        assert not form.is_valid()
        assert form.errors['__all__'][0].startswith(
            u'Password is too common.')


def test_user_creation_mismatch_passwords():
    """Test that password and password confirmation must match."""
    form = _submit_form(dict(password='sufficiantlycrypt0',
                             password_confirm='sufficiantlycrypto'))
    assert not form.is_valid()
    assert form.errors['__all__'][0].startswith(
        'Passwords do not match')


def test_user_creation_invalid_email():
    """Test that a user cannot be created with an invalid email address."""
    form = _submit_form(dict(email='totallyinvalidemail'))
    assert not form.is_valid()
    assert form.errors['email'][0].startswith(u'Enter a valid e-mail address.')
