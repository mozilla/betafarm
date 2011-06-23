from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^/$', 'projects.views.all', name='projects_all'),
    url(r'^/(?P<slug>[\w-]+)/$', 'projects.views.show', name='projects_show'),
)
