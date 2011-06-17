from django.conf import settings
from django.conf.urls.defaults import patterns, include

urlpatterns = patterns('',
    (r'', include('innovate.urls')),
    (r'', include('users.urls')),
    (r'^topics', include('topics.urls')),
)

# Handle 404 and 500 errors
handler404 = 'innovate.views.handle404'
handler500 = 'innovate.views.handle500'

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )

urlpatterns += patterns('',
    (r'^mockups/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': 'mockups',
        'show_indexes': True,
    })
)
