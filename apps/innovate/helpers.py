from jingo import register
from django.core.urlresolvers import reverse, resolve


@register.function
def active(request, url):
    path = u'/%s' % ('/'.join(request.path.split('/')[2:]),)
    if url.endswith(reverse('projects_all')):
        match = resolve(path)
        if match.url_name in (
            'projects_all', 'projects_show', 'projects_programs'):
            return ' selected'
    if path != '/' and url.startswith(path):
        return ' selected'
