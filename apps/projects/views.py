from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

import jingo

from tower import ugettext as _

from projects.models import Project
from feeds.models import Entry


def all(request):
    projects = Project.objects.exclude(tags__name='program').order_by('name')
    return jingo.render(request, 'projects/all.html', {
        'projects': projects,
        'view': 'all'
    })


def programs(request):
    programs = Project.objects.filter(tags__name='program').order_by('-name')
    return jingo.render(request, 'projects/programs.html', {
        'programs': programs,
    })


def show(request, slug):
    project = get_object_or_404(Project, slug=slug)
    topic = request.session.get('topic', None) or project.topics.all()[0].name
    return jingo.render(request, 'projects/show.html', {
        'project': project,
        'topic': topic
    })


@login_required
@require_POST
def follow(request, slug):
    project = get_object_or_404(Project, slug=slug)
    project.followers.add(request.user.get_profile())
    project.save()
    msg = _('Updates from <em>%s</em> will now appear in your dashboard.' % (
        project.name,))
    messages.success(request, msg)
    return HttpResponseRedirect(reverse('projects_show', kwargs={
        'slug': project.slug
    }))


@login_required
@require_POST
def unfollow(request, slug):
    project = get_object_or_404(Project, slug=slug)
    project.followers.remove(request.user.get_profile())
    project.save()
    msg = _('''Updates from <em>%s</em> will no longer appear in your
               dashboard''' % (project.name,))
    messages.success(request, msg)
    return HttpResponseRedirect(reverse('projects_show', kwargs={
        'slug': project.slug
    }))


def blog(request, slug):
    project = get_object_or_404(Project, slug=slug)
    entries = Entry.objects.filter(project=project).order_by('-published')
    paginator = Paginator(entries, 10)
    return jingo.render(request, 'projects/blog.html', {
        'project': project,
        'posts': paginator
    })


def active(request):
    projects = Project.objects.exclude(tags__name='program').order_by('-name')
    return jingo.render(request, 'projects/all.html', {
        'projects': projects,
        'view': 'active'
    })


def recent(request):
    projects = Project.objects.exclude(tags__name='program').order_by('-id')
    return jingo.render(request, 'projects/all.html', {
        'projects': projects,
        'view': 'recent'
    })
