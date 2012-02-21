from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^dashboard/$', 'users.views.dashboard', name='users_dashboard'),
    url(r'^signout/$', 'users.views.signout', name='users_signout'),
    url(r'^profile/edit/$', 'users.views.edit', name='users_edit'),
    url(r'^profile/edit/links/$', 'users.views.links',
        name='users_profile_links'),
    url(r'^profile/edit/link/delete/(?P<id>\d+)/$', 'users.views.delete_link',
        name='users_profile_delete_link'),
    url(r'^profile/edit/link/add/$', 'users.views.add_link',
        name='users_profile_add_link'),
    url(r'^profile/(?P<username>[\w-]+)/$', 'users.views.profile',
        name='users_profile'),
    url(r'^people/$', 'users.views.all', name='users_all'),
    url(r'^people/(?P<page>\d+)/$', 'users.views.all',
        name='users_all_page'),
    url(r'^people/recent/$', 'users.views.recent', name='users_recent'),
)
