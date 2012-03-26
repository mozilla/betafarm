from django.test import TestCase, Client
from django.contrib.auth.models import User

from users.models import Profile, Link
from projects.models import Project


class ProfileData(TestCase):

    def setUp(self):
        self.client = Client()
        self.User = User.objects.create(
            username=u'testaccount',
            password=u'password1',
            is_active=True
        )
        self.profile = Profile.objects.create(
            user=self.User
        )

    def test_social_links(self):
        user_slug = '/en-US/profile/%s/' % self.profile.user.username
        response = self.client.get(user_slug)
        self.assertEqual(len(response.context['social_links']), 0)

        Link.objects.create(
            name=u'Test',
            url=u'http://www.mozilla.org',
            profile=self.profile
        )

        response = self.client.get(user_slug)
        self.assertEqual(len(response.context['social_links']), 1)

    def test_project_links(self):
        user_slug = '/en-US/profile/%s/' % self.profile.user.username
        response = self.client.get(user_slug)
        self.assertEqual(response.context['projects'], False)

        p = Project.objects.create(
            name=u'Shipment of Fail',
            slug=u'shipment-of-fail',
            description=u'Blah',
            long_description=u'Blah blah'
        )

        p.team_members.add(self.profile)

        response = self.client.get(user_slug)
        self.assertNotEqual(response.context['projects'], False)
