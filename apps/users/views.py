from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from users.decorators import anonymous_only
from users.models import Profile
from users.utils import handle_profile_save

from tower import ugettext as _
import jingo


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


def profile(request, username):
    user = get_object_or_404(auth.models.User, username=username)
    profile = get_object_or_404(Profile, user=user)
    return jingo.render(request, 'users/profile.html', {
        'profile': profile
    })


@login_required
def edit(request):
    form = handle_profile_save(request)
    if form.is_valid():
        return HttpResponseRedirect(reverse('users_profile', kwargs={
            'username': request.user.username
        }))
    return jingo.render(request, 'users/edit.html', {
        'form': form
    })


def all(request):
    """Display a paginated, searchable list of users."""
    # TODO - Implement page argument
    profiles = Profile.objects.all()
    paginator = Paginator(profiles, 15)
    return jingo.render(request, 'users/all.html', {
        'paginator': paginator,
        'profiles': paginator.page(1).object_list,
        'page': 'all'
    })


def active(request):
    """Display a list of the most active users."""
    # TODO - We don't have anything with which to measure activity yet.
    profiles = Profile.objects.all().order_by('-user__last_login')
    paginator = Paginator(profiles, 15)
    return jingo.render(request, 'users/all.html', {
        'paginator': paginator,
        'profiles': paginator.page(1).object_list,
        'page': 'active'
    })


def recent(request):
    """Display a list of the most recent users."""
    profiles = Profile.objects.all().order_by('-user__date_joined')
    paginator = Paginator(profiles, 15)
    return jingo.render(request, 'users/all.html', {
        'paginator': paginator,
        'profiles': paginator.page(1).object_list,
        'page': 'recent'
    })


def staff(request):
    """Display a list of staff users."""
    profiles = Profile.objects.filter(staff=True)
    paginator = Paginator(profiles, 15)
    return jingo.render(request, 'users/all.html', {
        'paginator': paginator,
        'profiles': paginator.page(1).object_list,
        'page': 'all'
    })
