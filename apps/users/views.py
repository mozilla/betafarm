from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from users.models import Profile
from users.utils import handle_profile_save

import jingo


def signout(request):
    """Sign the user out, destroying their session."""
    auth.logout(request)
    return HttpResponseRedirect(reverse('innovate_splash'))


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


def all(request, page=1):
    """Display a paginated, searchable list of users."""
    paginator = Paginator(Profile.objects.all(), 15)
    return jingo.render(request, 'users/all.html', {
        'paginator': paginator,
        'profiles': paginator.page(page),
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
