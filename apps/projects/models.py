from django.conf import settings
from django.db import models

from tower import ugettext_lazy as _
from taggit.managers import TaggableManager

from users.models import Profile


class Link(models.Model):
    name = models.CharField(verbose_name=_(u'Name'), max_length=100)
    url = models.URLField(verbose_name=_(u'URL'))
    subscribe = models.BooleanField(default=False)
    blog = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s -> %s' % (self.name, self.url)


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
    links = models.ManyToManyField(Link, verbose_name=_(u'Links'),
                                   null=True, blank=True)
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
    def nav_links(self):
        return self.links.filter(blog=True)

    @property
    def other_links(self):
        return self.links.filter(blog=False)

    @property
    def is_program(self):
        return len(self.tags.filter(name='program'))

    def __unicode__(self):
        return self.name
