# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from innovate.utils import get_partition_id, safe_filename, ImageStorage

from django_browserid.auth import default_username_algo
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
    name = models.CharField(max_length=50, verbose_name=_(u'Link Name'))
    url = models.URLField(verbose_name=_(u'URL'), max_length=255)
    profile = models.ForeignKey('users.Profile', blank=True, null=True)

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
    featured = models.BooleanField(default=False)
    featured_image = models.ImageField(verbose_name=_(u'Featured Image'),
                                       blank=True, null=True,
                                       upload_to=settings.USER_AVATAR_PATH)

    @models.permalink
    def get_absolute_url(self):
        return ('users_profile', (), {
            'username': self.user.username,
        })

    def owns_project(self, project):
        return self.user.is_superuser or (project in self.projects_owned.all())

    def follows_project(self, project):
        return project in self.projects_following.all()

    @property
    def avatar_or_default(self):
        """Return user provided avatar, or default if none exists."""
        return self.avatar or 'img/user-default.jpg'

    @property
    def featured_image_or_default(self):
        """Return featured image for splash page."""
        return self.featured_image or 'img/featured-default.gif'

    def __unicode__(self):
        """Return a string representation of the user."""
        return self.display_name

    @property
    def username_hash(self):
        """
        Return a hash of the users email. Used as a URL component when no
        username is set (as is the case with users signed up via BrowserID).
        """
        return default_username_algo(self.user.email)

    @property
    def has_chosen_identifier(self):
        """Determine if user has a generated or chosen public identifier.."""
        return self.name or (not self.user.username == self.username_hash)

    @property
    def masked_email(self):
        """
        If a user does not have a display name or a username, their email may
        be displayed on their profile. This returns a masked copy so we don't
        leak that data.
        """
        user, domain = self.user.email.split('@')
        mask_part = lambda s, n: s[:n] + u'…' + s[-1:]
        return '@'.join(
            (mask_part(user, len(user) / 3),
             mask_part(domain, 1)))

    @property
    def display_name(self):
        """Choose and return the best public display identifier for a user."""
        if self.name:
            return self.name
        if self.has_chosen_identifier:
            return self.user.username
        return self.masked_email
