from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',

    # Sign in / Sign up
    url(r'^signin/$', 'users.views.signin', name='users_signin'),
    url(r'^signup/$', 'users.views.signup', name='users_signup'),
    url(r'^signout/$', 'users.views.signout', name='users_signout'),
    url(r'^confirm/(?P<confirmation_token>\w+)$',
        'users.views.confirm', name='users_confirm'),

    # Reset password urls
    url(r'^forgot/$', 'users.views.password_reset',
        name='users_forgot_password'),
    url(r'^forgot/sent/$', 'users.views.password_reset_done',
        name='users_forgot_password_done'),
    url(r'^forgot/(?P<uidb36>\w{1,13})/(?P<token>\w{1,13}-\w{1,20})/$',
        'users.views.password_reset_confirm',
        name='users_forgot_password_confirm'),

    # Profile urls
    url(r'^profile/(?P<username>[\w-]+)/$', 'users.views.profile',
        name='users_profile'),
)
