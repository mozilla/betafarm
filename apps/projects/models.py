from django.conf import settings
from django.db import models

from django_push.subscriber.models import Subscription

from tower import ugettext_lazy as _
from taggit.managers import TaggableManager

from innovate.models import BaseModel
from users.models import Profile


class Project(BaseModel):
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
    owners = models.ManyToManyField(Profile,
                                    verbose_name=_(u'Project Owners'),
                                    related_name=u'projects_owned')
    team_members = models.ManyToManyField(Profile,
                                          verbose_name=_(u'Team Members'))
    topics = models.ManyToManyField('topics.Topic', verbose_name=_(u'Topics'))
    featured = models.BooleanField(default=False)
    followers = models.ManyToManyField(Profile,
                                       verbose_name=_(u'Followers'),
                                       related_name=u'projects_following')

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
    def image_or_default(self):
        return self.image or 'img/project-default.gif'

    @property
    def featured_image_or_default(self):
        return self.featured_image or 'img/featured-default.gif'

    @property
    def active_topics(self):
        return self.topics.filter(draft=False)

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


class Link(BaseModel):
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
    featured = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s -> %s' % (self.name, self.url)
