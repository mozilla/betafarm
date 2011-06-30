import jingo

from events.models import Event


def all(request):
    events = Event.objects.all()
    return jingo.render(request, 'events/all.html', {
        'events': events
    })
