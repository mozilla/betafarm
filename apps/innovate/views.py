import jingo


def splash(request):
    return jingo.render(request, 'innovate/splash.html', {
        'featured_project': None,
        'featured_event': None,
        'featured_person': None,
    })
