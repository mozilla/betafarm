import random

import jingo

from users.models import Profile
from projects.models import Project


def splash(request):
    projects = Project.objects.filter(featured=True)
    project = projects and random.choice(projects) or None
    users = Profile.objects.filter(featured=True)
    user = users and random.choice(users) or None
    return jingo.render(request, 'innovate/splash.html', {
        'featured_project': project,
        'featured_event': None,
        'featured_user': user,
    })


def handle404(request):
    return jingo.render(request, 'handlers/404.html')


def handle500(request):
    return jingo.render(request, 'handlers/500.html')
