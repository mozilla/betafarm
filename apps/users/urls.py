from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^signout/$', 'users.views.signout', name='users_signout'),
    url(r'^profile/edit/$', 'users.views.edit', name='users_edit'),
    url(r'^profile/(?P<username>[\w-]+)/$', 'users.views.profile',
        name='users_profile'),
    url(r'^people/$', 'users.views.all', name='users_all'),
    url(r'^people/active/$', 'users.views.active', name='users_active'),
    url(r'^people/recent/$', 'users.views.recent', name='users_recent'),
)
