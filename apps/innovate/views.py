import jingo

from innovate.utils import get_blog_feed_entries
from projects.models import Project


def splash(request):
    """Display splash page. With featured projects and news feed."""
    projects = Project.objects.filter(featured=True)[:4]
    return jingo.render(request, 'innovate/splash.html', {
        'featured_projects': projects,
        'blog_entries': get_blog_feed_entries(),
    })


def about(request):
    """Display the about page. Simple direct to template."""
    # NOTE: can't use ``django.views.generic.simple.direct_to_template``
    # because we use jinja2 templates instead of Django templates.
    return jingo.render(request, 'innovate/about.html')


def handle404(request):
    """Handle 404 responses."""
    return jingo.render(request, 'handlers/404.html', status=404)


def handle500(request):
    """Handle server errors."""
    return jingo.render(request, 'handlers/500.html', status=500)
