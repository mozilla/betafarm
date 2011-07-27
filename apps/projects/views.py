from django.shortcuts import get_object_or_404

import jingo

from projects.models import Project


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
