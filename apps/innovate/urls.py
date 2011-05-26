from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'innovate.views.splash', name='innovate_splash'),
)
