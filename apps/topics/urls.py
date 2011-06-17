from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^/$', 'topics.views.all', name='topics_all'),
    url(r'^(?P<slug>[\w-]+)/$', 'topics.views.show', name='topics_show'),
)
