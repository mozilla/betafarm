import datetime

from django.contrib import admin
from django.db import models


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
