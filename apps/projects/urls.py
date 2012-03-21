from __future__ import absolute_import
from django.conf.urls.defaults import patterns, url

from .views import (AddProjectLinkView, DeleteProjectLinkView, EditProjectView,
                    ListProjectLinksView)


urlpatterns = patterns('',
    url(r'^projects/$', 'projects.views.all', name='projects_all'),
    url(r'^projects/recent/$', 'projects.views.recent',
        name='projects_recent'),
    url(r'^projects/links/delete/(?P<pk>\d+)/$',
        DeleteProjectLinkView.as_view(),
        name='projects_links_delete'),
    url(r'^projects/(?P<slug>[\w]+)/$', 'projects.views.topic',
        name='projects_topic'),
    url(r'^(?P<slug>[\w-]+)/$', 'projects.views.show', name='projects_show'),
    url(r'^(?P<slug>[\w-]+)/follow/$', 'projects.views.follow',
        name='projects_follow'),
    url(r'^(?P<slug>[\w-]+)/unfollow/$', 'projects.views.unfollow',
        name='projects_unfollow'),
    url(r'^(?P<slug>[\w-]+)/edit/$',
        EditProjectView.as_view(),
        name='projects_edit'),
    url(r'^(?P<slug>[\w-]+)/links/$', ListProjectLinksView.as_view(),
        name='projects_links_list'),
    url(r'^(?P<slug>[\w-]+)/links/add/$', AddProjectLinkView.as_view(),
        name='projects_links_add'),
)
