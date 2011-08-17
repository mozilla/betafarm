import random

import jingo

from users.models import Profile
from projects.models import Project
from events.models import Event
from feeds.models import Entry


def splash(request):
    def get_random(cls, **kwargs):
        choices = cls.objects.filter(**kwargs)
        return choices and random.choice(choices) or None
    return jingo.render(request, 'innovate/splash.html', {
        'featured_project': get_random(Project, featured=True),
        'featured_event': get_random(Event, featured=True),
        'featured_user': get_random(Profile, featured=True),
        'entry': get_random(Entry, link__featured=True)
    })


def about(request):
    return jingo.render(request, 'innovate/about.html')


def handle404(request):
    return jingo.render(request, 'handlers/404.html')


def handle500(request):
    return jingo.render(request, 'handlers/500.html')
