import datetime

from django.contrib import admin
from django.db import models

from innovate.models import BaseModel


class Entry(BaseModel):
    title = models.CharField(max_length=100)
    published = models.DateTimeField(default=datetime.datetime.now())
    url = models.URLField()
    body = models.TextField()
    link = models.ForeignKey('projects.Link')

    class Meta:
        verbose_name_plural = u'entries'

    def __unicode__(self):
        return u'%s -> %s' % (self.title, self.url)

    @property
    def project(self):
        return self.link.project or None
admin.site.register(Entry)
