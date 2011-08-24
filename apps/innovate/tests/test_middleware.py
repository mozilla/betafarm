import fudge

from contextlib import contextmanager

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client


def get_users(filter_f=None):
    users = User.objects.all()
    assert len(users) > 0
    if not filter_f:
        return users
    filtered = filter(filter_f, users)
    assert len(filtered) > 0
    return filtered


@contextmanager
def user_with_generated_id(fake_auth, **kwargs):
    users = get_users(lambda u: not u.get_profile().has_chosen_identifier)
    fake_auth.expects_call().returns(users[0])
    yield


@contextmanager
def user_with_chosen_id(fake_auth, **kwargs):
    users = get_users(lambda u: u.get_profile().has_chosen_identifier)
    fake_auth.expects_call().returns(users[0])
    yield


class MiddlewareTests(TestCase):
    """
    Test `ProfileMiddleware`. Should ensure users have at least chosen a
    display name.
    """

    fixtures = ['users.json']

    def _get_and_follow_redirect(self, client, path):
        response = client.get(path)
        if response.status_code != 301:
            return response
        location = response.get('location', None)
        return client.get(location)

    @fudge.patch('django_browserid.auth.BrowserIDBackend.authenticate')
    def test_unsafe_paths(self, fake):
        with user_with_generated_id(fake):
            client = Client()
            client.login()
            response = self._get_and_follow_redirect(client, '/')
            assert response.status_code == 302
            location = response.get('location', None)
            assert location.endswith(reverse('users_edit'))
            response = self._get_and_follow_redirect(client, '/projects/')
            assert response.status_code == 302
            location = response.get('location', None)
            assert location.endswith(reverse('users_edit'))

    @fudge.patch('django_browserid.auth.BrowserIDBackend.authenticate')
    def test_safe_paths(self, fake):
        with user_with_generated_id(fake):
            client = Client()
            client.login()
            expect_ok = (
                self._get_and_follow_redirect(client, reverse('users_edit')),
                self._get_and_follow_redirect(
                    client, reverse('django.views.static.serve', kwargs={
                        'path': '/media/css/innovate/main.css'
                    })
                ),
                self._get_and_follow_redirect(
                    client, reverse('users_profile_add_link')),
                self._get_and_follow_redirect(
                    client, reverse('users_profile_links')),
                self._get_and_follow_redirect(
                    client, reverse('users_profile_delete_link', kwargs={
                        'id': 1,
                    })
                )
            )
            for response in expect_ok:
                self.assertEqual(200, response.status_code)
            # users_signout is expected to 302 regardless.
            response = self._get_and_follow_redirect(
                client, reverse('users_signout'))
            self.assertEqual(302, response.status_code)
            location = response.get('location', None)
            self.assertEqual('http://testserver/', location)

    @fudge.patch('django_browserid.auth.BrowserIDBackend.authenticate')
    def test_user_with_chosen_id(self, fake):
        with user_with_chosen_id(fake):
            client = Client()
            client.login()
            response = self._get_and_follow_redirect(client, '/')
            assert response.status_code == 200
            response = self._get_and_follow_redirect(client, '/projects/')
            assert response.status_code == 200
