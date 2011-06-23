from django.shortcuts import get_object_or_404

import jingo

from projects.models import Project


def all(request):
    projects = Project.objects.all()
    return jingo.render(request, 'projects/all.html', {
        'projects': projects,
    })


def show(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if 'topic' in request.session:
        topic = request.session.get('topic')
    else:
        topics = project.topics.all()
        topic = topics[0].name
    return jingo.render(request, 'projects/show.html', {
        'project': project,
        'topic': topic
    })
