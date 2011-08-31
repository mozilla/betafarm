from django.db import models

from innovate.models import BaseModel


class Activity(BaseModel):
    entry = models.ForeignKey('feeds.Entry', blank=True, null=True,
                              unique=True)
    published_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%d: Entry: %s' % (self.pk, self.entry)


def broadcast(source):
    return Activity.objects.create(
        entry=source
    )
