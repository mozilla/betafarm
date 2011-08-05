from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_delete

from django_push.subscriber.models import Subscription
from django_push.subscriber.signals import updated

from tower import ugettext_lazy as _
from taggit.managers import TaggableManager

from projects import tasks
from users.models import Profile


class Project(models.Model):
    name = models.CharField(verbose_name=_(u'Name'), max_length=100)
    slug = models.SlugField(verbose_name=_(u'Slug'), unique=True,
                            max_length=100)
    description = models.CharField(verbose_name=_(u'Description'),
                                   max_length=200)
    long_description = models.TextField(verbose_name=_(u'Long Description'))
    image = models.ImageField(verbose_name=_(u'Image'), blank=True,
                              upload_to=settings.PROJECT_IMAGE_PATH,
                              null=True)
    featured_image = models.ImageField(verbose_name=_(u'Featured Image'),
                                       blank=True, null=True,
                                       upload_to=settings.PROJECT_IMAGE_PATH)
    team_members = models.ManyToManyField(Profile,
                                          verbose_name=_(u'Team Members'))
    topics = models.ManyToManyField('topics.Topic', verbose_name=_(u'Topics'))
    featured = models.BooleanField(default=False)

    tags = TaggableManager(blank=True)

    @property
    def image_or_default(self):
        return self.image or 'img/project-default.gif'

    @property
    def featured_image_or_default(self):
        return self.featured_image or 'img/featured-default.gif'

    @property
    def blog(self):
        blog = self.link_set.filter(blog=True)
        return blog and blog[0] or None

    @property
    def nav_links(self):
        return self.link_set.filter(blog=True)

    @property
    def other_links(self):
        return self.link_set.filter(blog=False)

    @property
    def is_program(self):
        return len(self.tags.filter(name='program'))

    def __unicode__(self):
        return self.name


class Link(models.Model):
    """
    A link that can be added to a project. Links can be 'subscribed' to, in
    which case, entries from the links RSS/Atom feed will be syndicated.
    """
    name = models.CharField(verbose_name=_(u'Name'), max_length=100)
    url = models.URLField(verbose_name=_(u'URL'))
    subscribe = models.BooleanField(default=False)
    blog = models.BooleanField(default=False)
    subscription = models.ForeignKey(Subscription, null=True, blank=True)
    project = models.ForeignKey(Project, null=True, blank=True)

    def __unicode__(self):
        return u'%s -> %s' % (self.name, self.url)


def link_subscriber(sender, instance, created, **kwargs):
    """Subscribe to link RSS/Atom feed."""
    if not isinstance(instance, Link) or not instance.subscribe:
        return
    if instance.subscription:
        return
    tasks.PushSubscriber.apply_async(args=(instance,))
post_save.connect(link_subscriber, sender=Link)


def link_delete_handler(sender, instance, **kwargs):
    """Send unsubscribe request to link hub."""
    if not isinstance(instance, Link):
        return
    tasks.PushUnsubscriber.apply_async(args=(instance,))
pre_delete.connect(link_delete_handler, sender=Link)


def notification_listener(notification, **kwargs):
    """Create entries for notification."""
    sender = kwargs.get('sender', None)
    if not sender:
        return
    tasks.PushNotificationHandler.apply_async(args=(notification, sender))
updated.connect(notification_listener)
