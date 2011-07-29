from django.db import models


class Entry(models.Model):
    title = models.CharField(max_length=100)
    link = models.URLField()
    body = models.TextField()
    project = models.ForeignKey('projects.Project')
