from django.conf import settings
from django.db import models

from tower import ugettext_lazy as _


class Topic(models.Model):
    name = models.CharField(verbose_name=_(u'Name'), max_length=100)
    slug = models.SlugField(verbose_name=_(u'Slug'), unique=True,
                            max_length=100)
    description = models.CharField(verbose_name=_(u'Description'),
                                   max_length=100)
    image = models.ImageField(verbose_name=_(u'Image'), blank=True,
                              upload_to=settings.TOPIC_IMAGE_PATH, null=True,
                              max_length=settings.MAX_FILEPATH_LENGTH)

    def __unicode__(self):
        return self.name
