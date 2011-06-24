import random

import jingo

from projects.models import Project


def splash(request):
    project = random.choice(Project.objects.filter(featured=True))
    return jingo.render(request, 'innovate/splash.html', {
        'featured_project': project,
        'featured_event': None,
        'featured_person': None,
    })


def handle404(request):
    return jingo.render(request, 'handlers/404.html')


def handle500(request):
    return jingo.render(request, 'handlers/500.html')
