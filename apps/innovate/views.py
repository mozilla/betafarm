import random

import jingo

from users.models import Profile
from projects.models import Project
from events.models import Event
from feeds.models import Entry


def splash(request):
    def get_random(cls):
        choices = cls.objects.filter(featured=True)
        return choices and random.choice(choices) or None
    entry = random.choice(Entry.objects.all())
    return jingo.render(request, 'innovate/splash.html', {
        'featured_project': get_random(Project),
        'featured_event': get_random(Event),
        'featured_user': get_random(Profile),
        'entry': entry
    })


def about(request):
    return jingo.render(request, 'innovate/about.html')


def handle404(request):
    return jingo.render(request, 'handlers/404.html')


def handle500(request):
    return jingo.render(request, 'handlers/500.html')
