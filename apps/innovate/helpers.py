from django.core.urlresolvers import resolve
from django.http import Http404

from jingo import register


URL_NAV_NAMES = {
    'innovate_splash': 'home',
    'innovate_about': 'about',
    'innovate_hatchery': 'hatchery',
    'projects_': 'projects',
    'users_': 'users',
}


@register.function
def active_name(request):
    # strip locale
    path = u'/%s' % ('/'.join(request.path.split('/')[2:]),)
    try:
        match = resolve(path)
    except Http404:
        return ''
    for name in URL_NAV_NAMES:
        if match.url_name.startswith(name):
            return URL_NAV_NAMES[name]
    return ''
