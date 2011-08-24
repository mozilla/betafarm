import random

import jingo

from users.models import Profile
from projects.models import Project
from events.models import Event
from feeds.models import Entry


def splash(request):
    """Display splash page. With featured project, event, person, blog post."""
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
    """Display the about page. Simple direct to template."""
    # NOTE: can't use ``django.views.generic.simple.direct_to_template``
    # because we use jinja2 templates instead of Django templates.
    return jingo.render(request, 'innovate/about.html')


def handle404(request):
    """Handle 404 responses."""
    return jingo.render(request, 'handlers/404.html')


def handle500(request):
    """Handle server errors."""
    return jingo.render(request, 'handlers/500.html')
