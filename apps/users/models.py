import datetime
import hashlib
import random

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import mail
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import render_to_string

from tower import ugettext_lazy as _


def create_confirmation_token(username):
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    return hashlib.sha1(salt + username).hexdigest()


class ProfileManager(models.Manager):

    def create_profile(self, username, email, password, **kwargs):
        """Create a new user profile."""
        now = datetime.datetime.now()
        user = User(username=username, email=email, is_staff=False,
                    is_active=False, is_superuser=False, last_login=now,
                    date_joined=now)
        user.set_password(password)
        user.save()
        try:
            confirmation_token = create_confirmation_token(username)
            profile = self.create(user=user,
                                  confirmation_token=confirmation_token,
                                  **kwargs)
            return profile
        except:
            # delete the user account if anything went wrong, so that we're
            # not left with stale records in auth_user. TODO - watch out for
            # race conditions here.
            user.delete()
            raise


class Link(models.Model):
    SUPPORTED_SERVICES = (
        ('github', 'Github'),
        ('flickr', 'Flickr'),
        ('twitter', 'Twitter')
    )
    service = models.CharField(max_length=50, verbose_name=_(u'Service Name'),
                               choices=SUPPORTED_SERVICES)
    name = models.CharField(max_length=50, verbose_name=_(u'Link Name'))
    url = models.URLField(verbose_name=_(u'URL'), max_length=255)

    def __unicode__(self):
        return u'%s -> %s' % (self.name, self.url)


class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True,
                                verbose_name=_(u'User'))
    name = models.CharField(max_length=255, blank=True,
                            verbose_name=_(u'Display name'))
    avatar = models.ImageField(upload_to=settings.USER_AVATAR_PATH, null=True,
                               blank=True, verbose_name=_(u'Avatar'),
                               max_length=settings.MAX_FILEPATH_LENGTH)
    website = models.URLField(verbose_name=_(u'Website'), max_length=255,
                              blank=True)
    bio = models.TextField(verbose_name=_(u'Bio'), blank=True)
    confirmation_token = models.CharField(
        verbose_name=_(u'Confirmation Token'), max_length=40)
    links = models.ManyToManyField(Link, verbose_name=_(u'Links'))

    objects = ProfileManager()

    def send_confirmation_email(self):
        current_site = Site.objects.get_current()
        url = reverse('users.views.confirm',
                      args=[self.confirmation_token])
        email_kwargs = {
            'domain': current_site.domain,
            'confirm_url': url,
        }
        message = render_to_string('users/email/confirm_email.txt',
                                   email_kwargs)
        subject = _('Confirm Registration')
        mail.send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                       [self.user.email])

    def __unicode__(self):
        return unicode(self.user)
