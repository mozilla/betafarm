from django.db import models

from tower import ugettext_lazy as _

from users.models import Profile


class Event(models.Model):
    name = models.CharField(verbose_name=_(u'Event Name'),
                            max_length=100)
    slug = models.SlugField(verbose_name=_(u'Slug'), unique=True,
                            max_length=100)
    start = models.DateTimeField(verbose_name=_(u'Start Date'))
    end = models.DateTimeField(verbose_name=_(u'End Date'))
    description = models.TextField(verbose_name=_(u'Description'))
    attendees = models.ManyToManyField(Profile, verbose_name=_(u'Attendees'),
                                       blank=True)

    def __unicode__(self):
        return self.name
