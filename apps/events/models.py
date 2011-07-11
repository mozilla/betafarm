from django.conf import settings
from django.db import models

from tower import ugettext_lazy as _

from users.models import Profile


class Venue(models.Model):
    name = models.CharField(verbose_name=_(u'Name'), max_length=100)
    slug = models.SlugField(verbose_name=_(u'URL Slug'), unique=True,
                            max_length=100)
    address = models.CharField(verbose_name=_(u'Street Address 1'),
                               max_length=150, blank=True)
    address_two = models.CharField(verbose_name=_(u'Street Address 2'),
                                   max_length=150, blank=True)
    city = models.CharField(verbose_name=_(u'City'), max_length=100,
                            blank=True)
    state = models.CharField(verbose_name=_(u'State/Province'), max_length=100,
                                            blank=True)
    zip_code = models.CharField(verbose_name=_(u'Zip/Postal Code'),
                                max_length=15, blank=True)
    country = models.CharField(verbose_name=_(u'Country'), max_length=100,
                               blank=True)

    def __unicode__(self):
        return self.name


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
    venue = models.ForeignKey(Venue, null=True, default=None)
    featured = models.BooleanField(
        verbose_name=_(u'Featured?'), default=False,
        help_text=_(u'Display this event on the splash page'))
    featured_image = models.ImageField(
        verbose_name=_(u'Featured Image'),
        blank=True, null=True, upload_to=settings.EVENT_IMAGE_PATH,
        help_text=_(u'This image will appear on the splash page if this ' +
                    'is a featured project'))
    created_by = models.ForeignKey('users.Profile', related_name='events',
                                   null=True, default=None)

    @property
    def featured_image_or_default(self):
        return self.featured_image or 'featured-default.gif'

    def __unicode__(self):
        return self.name
