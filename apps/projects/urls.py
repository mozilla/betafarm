from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^projects/$', 'projects.views.all', name='projects_all'),
    url(r'^programs/$', 'projects.views.programs', name='projects_programs'),
    url(r'^projects/active/$', 'projects.views.active',
        name='projects_active'),
    url(r'^projects/recent/$', 'projects.views.recent',
        name='projects_recent'),
    url(r'^(?P<slug>[\w-]+)/$', 'projects.views.show', name='projects_show'),
    url(r'^(?P<slug>[\w-]+)/follow/$', 'projects.views.follow',
        name='projects_follow'),
    url(r'^(?P<slug>[\w-]+)/unfollow/$', 'projects.views.unfollow',
        name='projects_unfollow'),
    url(r'^(?P<slug>[\w-]+)/activity/$', 'projects.views.activity',
        name='projects_activity'),
    url(r'^(?P<slug>[\w-]+)/activity/(?P<page>\d+)/$',
        'projects.views.activity_page',
        name='projects_activity_page')
)
