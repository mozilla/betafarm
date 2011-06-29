from django.shortcuts import get_object_or_404

import jingo

from projects.models import Project
from topics.models import Topic


def all(request):
    """Show a list of topics."""
    # note that we get the list of topics from the bundled context processor
    projects = Project.objects.all()
    projects_count = projects.count()
    return jingo.render(request, 'topics/all.html', {
        'projects': projects,
        'projects_count': projects_count,
    })


def show(request, slug):
    """Show a specific topic."""
    topic = get_object_or_404(Topic, slug=slug)
    projects = Project.objects.filter(topics=topic)
    request.session['topic'] = topic.name
    return jingo.render(request, 'topics/show.html', {
        'topic': topic,
        'projects': projects
    })
