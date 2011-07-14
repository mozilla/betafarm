import random

import jingo

from users.models import Profile
from projects.models import Project
from events.models import Event


def splash(request):
    def get_random(cls):
        choices = cls.objects.filter(featured=True)
        return choices and random.choice(choices) or None
    return jingo.render(request, 'innovate/splash.html', {
        'featured_project': get_random(Project),
        'featured_event': get_random(Event),
        'featured_user': get_random(Profile),
    })


def about(request):
    return jingo.render(request, 'innovate/about.html')


def programs(request):
    return jingo.render(request, 'innovate/programs.html')


def handle404(request):
    return jingo.render(request, 'handlers/404.html')


def handle500(request):
    return jingo.render(request, 'handlers/500.html')
