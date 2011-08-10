import datetime

from django.contrib import admin
from django.db import models
from django.db.models.signals import post_save

from activity.models import broadcast


class Entry(models.Model):
    title = models.CharField(max_length=100)
    published = models.DateTimeField(default=datetime.datetime.now())
    link = models.URLField()
    body = models.TextField()
    project = models.ForeignKey('projects.Project')

    class Meta:
        verbose_name_plural = u'entries'

    def __unicode__(self):
        return u'%s -> %s' % (self.title, self.link)
admin.site.register(Entry)


def entry_save_handler(sender, instance, **kwargs):
    broadcast(instance)
post_save.connect(entry_save_handler, sender=Entry)
