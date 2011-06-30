from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url('^/$', 'events.views.all', name='events_all'),
)
