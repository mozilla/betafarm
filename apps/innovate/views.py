import jingo


def splash(request):
    return jingo.render(request, 'innovate/splash.html', {
        'featured_project': None,
        'featured_event': None,
        'featured_person': None,
    })


def handle404(request):
    return jingo.render(request, 'handlers/404.html')


def handle500(request):
    return jingo.render(request, 'handlers/500.html')
