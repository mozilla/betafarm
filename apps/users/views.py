import json

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404

from activity.models import Activity
from users.models import Profile, Link
from users.forms import ProfileForm, ProfileLinksForm

import jingo

ACTIVITY_PAGE_SIZE = 20


@login_required
def dashboard_activity(request, page=1):
    """Display a single page of activities for a users dashboard."""
    start = int(page) * ACTIVITY_PAGE_SIZE
    end = start + ACTIVITY_PAGE_SIZE
    profile = request.user.get_profile()
    activities = Activity.objects.filter(
        entry__link__project__in=profile.projects_following.all()
    ).select_related('entry', 'entry__link', 'entry__link__project').order_by(
        '-published_on')[start:end]
    if not activities:
        raise Http404
    return jingo.render(request, 'activity/activity.html', {
        'activities': activities,
        'show_meta': True,
    })


@login_required
def dashboard(request):
    """Display first page of activities for a users dashboard."""
    profile = request.user.get_profile()
    activities = Activity.objects.filter(
        entry__link__project__in=profile.projects_following.all()
    ).select_related(
        'entry', 'entry__link', 'entry__link__project'
    ).order_by('-published_on')
    has_more = len(activities) > ACTIVITY_PAGE_SIZE
    return jingo.render(request, 'users/dashboard.html', {
        'profile': profile,
        'activities': activities[:ACTIVITY_PAGE_SIZE],
        'has_more': has_more
    })


def signout(request):
    """Sign the user out, destroying their session."""
    auth.logout(request)
    return HttpResponseRedirect(reverse('innovate_splash'))


def profile(request, username):
    """Display profile page for user specified by ``username``."""
    user = get_object_or_404(auth.models.User, username=username)
    profile = get_object_or_404(Profile, user=user)
    return jingo.render(request, 'users/profile.html', {
        'profile': profile
    })


@login_required
def links(request):
    if not request.is_ajax():
        raise Http404
    profile = request.user.get_profile()
    links = Link.objects.filter(profile=profile).order_by('id')
    return jingo.render(request, 'users/links.html', {
        'links': links
    })


@login_required
def delete_link(request, id):
    link = get_object_or_404(Link, pk=id)
    if request.user.get_profile() != link.profile:
        raise Http404
    if request.method == 'POST':
        link.delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(reverse('users_edit'))
    return jingo.render(request, 'users/profile_link_delete.html', {
        'link': link
    })


@login_required
def add_link(request):
    profile = request.user.get_profile()
    if request.method == 'POST':
        form = ProfileLinksForm(data=request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            link.profile = profile
            link.save()
            return HttpResponseRedirect(reverse('users_edit'))
        else:
            if request.is_ajax():
                return HttpResponse(json.dumps(form.errors), status=400)
            return jingo.render(request, 'users/profile_link_add.html', {
                'form': form
            })
    form = ProfileLinksForm()
    return jingo.render(request, 'users/profile_link_add.html', {
        'form': form
    })


@login_required
def edit(request):
    """Edit the currently logged in users profile."""
    profile = request.user.get_profile()
    if request.method == 'POST':
        form = ProfileForm(data=request.POST,
                           files=request.FILES,
                           instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            # adding in a link non-JS
            name = request.POST['link_name']
            url = request.POST['link_url']
            if not name == "" and not url == "":
                linksForm = ProfileLinksForm(data={
                    'url': url,
                    'name': name
                })
                if linksForm.is_valid():
                    link = linksForm.save(commit=False)
                    link.profile = profile
                    link.save()
            return HttpResponseRedirect(reverse('users_profile', kwargs={
                'username': request.user.username
            }))
    form = ProfileForm(instance=profile)
    links = profile.link_set.all()
    return jingo.render(request, 'users/edit.html', {
        'form': form,
        'links': links
    })


def all(request, page=1):
    """Display a paginated, searchable list of users."""
    # TODO - Implement support for search.
    profiles = Profile.objects.all().order_by('name')
    paginator = Paginator(profiles, 15)
    return jingo.render(request, 'users/all.html', {
        'paginator': paginator,
        'profiles': paginator.page(page),
        'page': 'all'
    })


def active(request, page=1):
    """Display a list of the most active users."""
    # TODO - We don't have anything with which to measure activity yet.
    profiles = Profile.objects.all().order_by('-user__last_login')
    paginator = Paginator(profiles, 15)
    return jingo.render(request, 'users/all.html', {
        'paginator': paginator,
        'profiles': paginator.page(page),
        'page': 'active'
    })


def recent(request, page=1):
    """Display a list of the most recent users."""
    profiles = Profile.objects.all().order_by('-user__date_joined')
    paginator = Paginator(profiles, 15)
    return jingo.render(request, 'users/all.html', {
        'paginator': paginator,
        'profiles': paginator.page(page),
        'page': 'recent'
    })
