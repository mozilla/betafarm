# -*- coding: utf-8 -*-

import base64
import hashlib

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from innovate.utils import get_partition_id, safe_filename, ImageStorage

from tower import ugettext_lazy as _


def determine_upload_path(instance, filename):
    chunk_size = 1000  # max files per directory
    path = getattr(settings, 'USER_AVATAR_PATH', 'images/profiles/')
    path = path.lstrip('/').rstrip('/')
    return "%(path)s/%(partition)d/%(filename)s" % {
        'path': path,
        'partition': get_partition_id(instance.pk, chunk_size),
        'filename': safe_filename(filename)
    }


class Link(models.Model):
    SUPPORTED_SERVICES = (
        (u'github', u'Github'),
        (u'flickr', u'Flickr'),
        (u'twitter', u'Twitter'),
        (u'other', u'Other')
    )
    service = models.CharField(max_length=50, verbose_name=_(u'Service Name'),
                               choices=SUPPORTED_SERVICES, default=u'other')
    name = models.CharField(max_length=50, verbose_name=_(u'Link Name'))
    url = models.URLField(verbose_name=_(u'URL'), max_length=255)

    def __unicode__(self):
        return u'%s -> %s' % (self.name, self.url)


def get_profile(cls):
    """Create an empty profile for users if none exists."""
    profile, created = Profile.objects.get_or_create(user=cls)
    return profile
User.get_profile = get_profile


class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True,
                                verbose_name=_(u'User'))
    name = models.CharField(max_length=255, blank=True,
                            verbose_name=_(u'Display name'))
    avatar = models.ImageField(upload_to=determine_upload_path, null=True,
                               blank=True, verbose_name=_(u'Avatar'),
                               max_length=settings.MAX_FILEPATH_LENGTH,
                               storage=ImageStorage())
    website = models.URLField(verbose_name=_(u'Website'), max_length=255,
                              blank=True)
    bio = models.TextField(verbose_name=_(u'Bio'), blank=True)
    links = models.ManyToManyField(Link, verbose_name=_(u'Links'), blank=True)
    staff = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    featured_image = models.ImageField(verbose_name=_(u'Featured Image'),
                                       blank=True, null=True,
                                       upload_to=settings.USER_AVATAR_PATH)

    @property
    def avatar_or_default(self):
        return self.avatar or 'img/person-default.gif'

    @property
    def featured_image_or_default(self):
        return self.featured_image or 'img/featured-default.gif'

    def __unicode__(self):
        return unicode(self.user)

    @property
    def has_chosen_identifier(self):
        """Determine if username has been automatically generated or chosen."""
        return not self.user.username == base64.urlsafe_b64encode(
            hashlib.sha1(self.user.email).digest()).rstrip('=')

    @property
    def masked_email(self):
        user, domain = self.user.email.split('@')
        mask_part = lambda s, n: s[:n] + u'…' + s[-1:]
        return '@'.join(
            (mask_part(user, len(user) / 3),
             mask_part(domain, 1)))

    @property
    def display_name(self):
        if self.name:
            return self.name
        if self.has_chosen_identifier:
            return self.user.username
        return self.masked_email
