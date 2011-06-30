from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url('^/$', 'events.views.all', name='events_all'),
    url('^/(?P<slug>[\w-]+)/$', 'events.views.show', name='events_show'),
    url('^/(?P<slug>[\w-]+)/attend/$', 'events.views.attend',
        name='events_attend'),
    url('^/(?P<slug>[\w-]+)/unattend/$', 'events.views.unattend',
        name='events_unattend'),
)
