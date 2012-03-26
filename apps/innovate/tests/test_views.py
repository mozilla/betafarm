from django.core.urlresolvers import reverse
from django.test import Client
from django.test.client import RequestFactory

from projects.models import Project
from innovate import urls
from innovate.views import handle404, handle500


def test_routes():
    c = Client()
    for pattern in urls.urlpatterns:
        response = c.get(reverse(pattern.name))
        assert response.status_code == 301
        assert response.has_header('location')
        location = response.get('location', None)
        assert location is not None
        response = c.get(location)
        assert response.status_code == 200


def test_featured():
    project = Project.objects.create(
        name=u'Test Project',
        slug=u'test-project',
        description=u'Blah',
        featured=True
    )
    c = Client()
    response = c.get('/en-US/')
    assert response.status_code == 200
    assert project.name in response.content.decode('utf8')


def test_404_handler():
    """Test that the 404 error handler renders and gives the correct code."""
    response = handle404(RequestFactory().get('/not/a/real/path/'))
    assert response.status_code == 404

def test_500_handler():
    """Test that the 500 error handler renders and gives the correct code."""
    response = handle500(RequestFactory().get('/not/a/real/path/'))
    assert response.status_code == 500
