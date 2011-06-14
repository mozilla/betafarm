from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^signin/$', 'users.views.signin', name='users_signin'),
    url(r'^signup/$', 'users.views.signup', name='users_signup'),
    url(r'^signout/$', 'users.views.signout', name='users_signout'),
    url(r'^confirm/(?P<confirmation_token>\w+)$',
        'users.views.confirm', name='users_confirm'),
)
