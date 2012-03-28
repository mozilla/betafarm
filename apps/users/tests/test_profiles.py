from django.test import TestCase
from django.contrib.auth.models import User

from commons.urlresolvers import reverse

from projects.models import Project
from topics.models import Topic
from users.models import Link, Profile


class ProfileData(TestCase):

    def setUp(self):
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


class ProfileViewTests(TestCase):
    def setUp(self):
        """Create user and a project with a topic."""
        self.password = 'lovezrugz'
        self.user = User.objects.create_user(
            username='TheDude',
            password=self.password,
            email='duder@aol.com',
        )
        self.profile = Profile.objects.create(user=self.user)
        self.owner_password = 'TheBumsLost'
        self.owner = User.objects.create_user(
            username='jlebowski',
            password=self.owner_password,
            email='jlebowski@aol.com',
        )
        self.owner_profile = Profile.objects.create(user=self.owner)
        self.topic = Topic.objects.create(
            name='Bowling',
            slug='bowling',
            description='League play.',
        )
        self.project = Project.objects.create(
            name='Get Rug Back',
            slug='rug-back',
            description='This aggression will not stand, man!',
            long_description='Not into the whole, brevity thing.',
        )
        self.project.topics.add(self.topic)
        self.project.team_members.add(self.profile)
        self.project.owners.add(self.owner_profile)

    def test_can_delete_profile(self):
        self.assertTrue(self.client.login(
            username=self.user.username,
            password=self.password
        ))
        resp = self.client.get(reverse('users_delete'), follow=True)
        self.assertContains(resp, 'Delete Profile')
        self.assertTrue(User.objects.get(username=self.user.username))
        self.assertTrue(Profile.objects.get(pk=self.profile.pk))
        resp = self.client.post(reverse('users_delete'), follow=True)
        self.assertTrue(resp.redirect_chain[-1][0].endswith('/en-US/'))
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username=self.user.username)
        with self.assertRaises(Profile.DoesNotExist):
            Profile.objects.get(pk=self.profile.pk)

    def test_delete_owner_not_delete_project(self):
        self.assertTrue(self.client.login(
            username=self.owner.username,
            password=self.owner_password
        ))
        self.assertEqual(self.project.owners.count(), 1)
        self.client.post(reverse('users_delete'), follow=True)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username=self.owner.username)
        with self.assertRaises(Profile.DoesNotExist):
            Profile.objects.get(pk=self.owner_profile.pk)
        self.assertEqual(self.project, Project.objects.get(pk=self.project.pk))
        self.assertEqual(self.project.owners.count(), 0)
