from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory

from projects.models import Project
from innovate import urls
from innovate.views import handle404, handle500


class ViewsTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_routes(self):
        for pattern in urls.urlpatterns:
            response = self.client.get(reverse(pattern.name))
            assert response.status_code == 301
            assert response.has_header('location')
            location = response.get('location', None)
            assert location is not None
            response = self.client.get(location)
            assert response.status_code == 200

    def test_featured(self):
        project, created = Project.objects.get_or_create(
            slug=u'test-project',
            defaults=dict(
                name=u'Test Project',
                description=u'Blah',
                featured=True,
            ),
        )
        response = self.client.get('/en-US/')
        assert response.status_code == 200
        assert project.name in response.content.decode('utf8')

    def test_404_handler(self):
        """Test that the 404 error handler gives the correct code."""
        response = handle404(RequestFactory().get('/not/a/real/path/'))
        assert response.status_code == 404

    def test_500_handler(self):
        """Test that the 500 error handler gives the correct code."""
        response = handle500(RequestFactory().get('/not/a/real/path/'))
        assert response.status_code == 500
