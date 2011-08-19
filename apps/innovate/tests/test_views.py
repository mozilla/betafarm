from django.core.urlresolvers import reverse
from django.test import Client

from projects.models import Project
from innovate import urls


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
    assert project.name in response.content
