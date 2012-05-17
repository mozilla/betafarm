import logging

from django.conf import settings
from django.db import models
from django.dispatch import receiver

import bleach
from tower import ugettext_lazy as _
from taggit.managers import TaggableManager

from users.models import Profile

BLEACH_FIELDS = ['long_description']
DEFAULT_INACTIVE_MESSAGE = _(u'This project is considered inactive.')

logger = logging.getLogger(__name__)


class ProjectQuerySet(models.query.QuerySet):
    def haz_topic(self):
        return self._clone().filter(topics__isnull=False).distinct()


class ProjectManager(models.Manager):
    def get_query_set(self):
        return ProjectQuerySet(self.model)

    def haz_topic(self):
        return self.get_query_set().haz_topic()


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
    inactive = models.BooleanField(default=False)
    owners = models.ManyToManyField(Profile,
                                    verbose_name=_(u'Project Owners'),
                                    related_name=u'projects_owned')
    team_members = models.ManyToManyField(Profile,
                                          blank=True,
                                          verbose_name=_(u'Team Members'))
    topics = models.ManyToManyField('topics.Topic', verbose_name=_(u'Topics'))
    featured = models.BooleanField(default=False)
    followers = models.ManyToManyField(Profile,
                                       blank=True,
                                       verbose_name=_(u'Followers'),
                                       related_name=u'projects_following')
    inactive_message = models.CharField(max_length=255, blank=True)

    objects = ProjectManager()
    tags = TaggableManager(blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ('projects_show', (), {
            'slug': self.slug
        })

    @models.permalink
    def get_edit_url(self):
        return ('projects_edit', (), {
            'slug': self.slug
        })

    @property
    def whole_team(self):
        """Return a list of unique project members and owners."""
        return list(set(self.owners.all()) | set(self.team_members.all()))

    @property
    def image_or_default(self):
        return self.image or 'img/project-default.gif'

    @property
    def featured_image_or_default(self):
        return self.featured_image or 'img/featured-default.gif'

    @property
    def inactive_message_or_default(self):
        return self.inactive_message or DEFAULT_INACTIVE_MESSAGE

    @property
    def active_topics(self):
        return self.topics.filter(draft=False)

    @property
    def active_topic_slugs(self):
        return ' '.join(t.slug for t in self.active_topics)

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

    def __unicode__(self):
        return self.name


class Link(models.Model):
    """
    A link that can be added to a project. Links can be 'subscribed' to, in
    which case, entries from the links RSS/Atom feed will be syndicated.
    """
    name = models.CharField(verbose_name=_(u'Name'), max_length=100)
    url = models.URLField(verbose_name=_(u'URL'))
    blog = models.BooleanField(default=False)
    project = models.ForeignKey(Project)
    featured = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s -> %s' % (self.name, self.url)


@receiver(models.signals.pre_save, sender=Project)
def strip_html(sender, instance, **kwargs):
    """Get rid of any bad HTML tags."""
    for field in BLEACH_FIELDS:
        cleaned_content = bleach.clean(unicode(getattr(instance, field)),
                                       tags=bleach.ALLOWED_TAGS + ['br', 'p'],
                                       strip=True)
        setattr(instance, field, cleaned_content)


@receiver(models.signals.post_delete, sender=Project)
def delete_images(sender, instance, **kwargs):
    """Delete the images when the project is deleted."""
    try:
        if instance.image:
            instance.image.delete(save=False)
    except OSError:
        logger.debug('Failed to delete image for %s', Project)

    try:
        if instance.featured_image:
            instance.featured_image.delete(save=False)
    except OSError:
        logger.debug('Failed to delete featured image for %s', Project)
