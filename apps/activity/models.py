from django.db import models


class Activity(models.Model):
    entry = models.ForeignKey('feeds.Entry', blank=True, null=True,
                              unique=True)
    published_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s:%s => %s' % (self.source_class, self.source_id, self.title)

    def from_feed(self):
        return self.entry != None


def broadcast(source):
    return Activity.objects.create(
        entry=source
    )
