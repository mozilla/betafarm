from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'innovate.views.splash', name='innovate_splash'),
    url(r'^programs/$', 'innovate.views.programs', name='innovate_programs'),
    url(r'^about/$', 'innovate.views.about', name='innovate_about'),
)
