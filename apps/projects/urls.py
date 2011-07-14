from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^/$', 'projects.views.all', name='projects_all'),
    url(r'^/active/$', 'projects.views.active', name='projects_active'),
    url(r'^/recent/$', 'projects.views.recent', name='projects_recent'),
    url(r'^/(?P<slug>[\w-]+)/$', 'projects.views.show', name='projects_show'),
)
