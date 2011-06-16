from django.contrib import auth
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from users.decorators import anonymous_only
from users.models import Profile
from users.utils import (handle_signin, handle_signup, get_next_url,
                         handle_password_reset, handle_password_reset_confirm)

from tower import ugettext as _
import jingo


@anonymous_only
def signin(request):
    """Sign the user in."""
    form = handle_signin(request)
    if request.user.is_authenticated():
        redirect_url = get_next_url(request) or reverse('innovate_splash')
        return HttpResponseRedirect(redirect_url)
    return jingo.render(request, 'users/signin.html', {
        'form': form,
    })


@anonymous_only
def signup(request):
    """Sign up form for new users."""
    form = handle_signup(request)
    if form.is_valid():
        return jingo.render(request, 'users/signup_done.html')
    return jingo.render(request, 'users/signup.html', dict(form=form))


def signout(request):
    """Sign the user out, destroying their session."""
    auth.logout(request)
    return HttpResponseRedirect(reverse('innovate_splash'))


@anonymous_only
def confirm(request, confirmation_token):
    """Confirm that a user is the owner of their email address."""
    profile = get_object_or_404(Profile, confirmation_token=confirmation_token)
    profile.user.is_active = True
    profile.user.save()
    messages.info(request, _('Thank you, you may now log in'))
    return HttpResponseRedirect(reverse('users_signin'))


@anonymous_only
def password_reset(request):
    form = handle_password_reset(request)
    if form.is_valid():
        return HttpResponseRedirect(reverse('users_forgot_password_done'))
    return jingo.render(request, 'users/password_reset.html', {'form': form})


@anonymous_only
def password_reset_done(request):
    return jingo.render(request, 'users/password_reset_sent.html')


@anonymous_only
def password_reset_confirm(request, uidb36, token):
    form = handle_password_reset_confirm(request, uidb36, token)
    if form.is_valid():
        messages.info(request, _('Your password has been updated. You '
                                 'should now be able to sign in.'))
        return HttpResponseRedirect(reverse('users_signin'))
    return jingo.render(request, 'users/password_reset_confirm.html', {
        'form': form,
        'token': token,
        'uidb36': uidb36,
    })
