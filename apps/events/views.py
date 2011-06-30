import jingo

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from events.models import Event


def all(request):
    events = Event.objects.all()
    return jingo.render(request, 'events/all.html', {
        'events': events
    })


def show(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return jingo.render(request, 'events/show.html', {
        'event': event
    })


@require_POST
@login_required
def attend(request, slug):
    event = get_object_or_404(Event, slug=slug)
    profile = request.user.get_profile()
    if profile not in event.attendees.all():
        event.attendees.add(profile)
        event.save()
    return HttpResponseRedirect(
        reverse('events_show', kwargs=dict(slug=slug)))


@require_POST
@login_required
def unattend(request, slug):
    event = get_object_or_404(Event, slug=slug)
    profile = request.user.get_profile()
    if profile in event.attendees.all():
        event.attendees.remove(profile)
        event.save()
    return HttpResponseRedirect(
        reverse('events_show', kwargs=dict(slug=slug)))
