from django.http import HttpResponse

import jingo

from topics.models import Topic


def all(request):
    """Show a list of topics."""
    topics = Topic.objects.all()
    return jingo.render(request, 'topics/all.html', {
        'topics': topics
    })


def show(request, slug):
    """Show a specific topic."""
    return HttpResponse('topics_show')
