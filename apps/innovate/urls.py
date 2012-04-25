from django.conf.urls.defaults import patterns, url
from django.views.generic.base import TemplateView


urlpatterns = patterns('',
    url(r'^/?$', 'innovate.views.splash', name='innovate_splash'),
    url(r'^about/$', 'innovate.views.about', name='innovate_about'),
    url(r'^search/$',
        TemplateView.as_view(template_name='innovate/search.html'),
        name='innovate_search'),
)
