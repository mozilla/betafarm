import os

from django.contrib.auth.models import User

import requests
from test_utils import TestCase, SkipTest

from commons.urlresolvers import reverse
from projects import cron
from projects.models import Project, Link
from topics.models import Topic
from users.models import Profile


class TestCron(TestCase):
    def test_get_isotope(self):
        try:
            requests.get('https://github.com/')
        except requests.ConnectionError:
            raise SkipTest('Could not connect to Github.')
        if os.path.exists(cron.ISOTOPE_PATH):
            os.remove(cron.ISOTOPE_PATH)
        self.assertFalse(os.path.exists(cron.ISOTOPE_PATH))
        cron.get_isotope()
        self.assertTrue(os.path.exists(cron.ISOTOPE_PATH))


class TestViews(TestCase):
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
        self.project_xss = Project.objects.create(
            name='Get Rug Back',
            slug='rug-back-b',
            description='This aggression will not stand, man!',
            long_description="<script>alert('i am evil');</script>",
        )
        self.project.topics.add(self.topic)
        self.project.team_members.add(self.profile)
        self.project.owners.add(self.owner_profile)

    def test_view_all(self):
        """Make sure the list all view displays our project."""
        resp = self.client.get(reverse('projects_all'), follow=True)
        self.assertContains(resp, self.project.name)

        # make sure only projects with at least one topic are shown
        self.project.topics.remove(self.topic)
        self.project.save()
        resp = self.client.get(reverse('projects_all'), follow=True)
        self.assertNotContains(resp, self.project.name)

    def test_view_one(self):
        """Test that the project detail page works."""
        resp = self.client.get(self.project.get_absolute_url(), follow=True)
        self.assertContains(resp, self.project.name)
        self.assertContains(resp, self.project.long_description)

    def test_user_owner_and_team_member_shows_once(self):
        """Test that if a user is added as a member and and owner
        that they only show up once on the project page"""
        self.project.owners.add(self.profile)
        resp = self.client.get(self.project.get_absolute_url(), follow=True)
        self.assertContains(resp, self.profile.get_absolute_url(), 1)

    def test_following(self):
        """Test that users can follow projects."""
        self.assertTrue(self.client.login(
            username=self.user.username,
            password=self.password
        ))
        resp = self.client.get(self.project.get_absolute_url(), follow=True)
        self.assertEqual(resp.context['project'].followers.count(), 0)
        resp = self.client.post(
            reverse('projects_follow', kwargs={'slug': self.project.slug}),
            follow=True,
        )
        self.assertEqual(resp.context['project'].followers.count(), 1)

    def test_unfollowing(self):
        """Test that users can stop following projects."""
        self.test_following()
        resp = self.client.post(
            reverse('projects_unfollow', kwargs={'slug': self.project.slug}),
            follow=True,
        )
        self.assertEqual(resp.context['project'].followers.count(), 0)

    def test_owner_sees_edit_button(self):
        """Test that only a project owner can see the edit button"""
        resp = self.client.get(self.project.get_absolute_url(), follow=True)
        self.assertContains(resp, self.project.name)
        self.assertContains(resp, self.project.long_description)
        self.assertNotContains(resp, self.project.get_edit_url())
        self.assertTrue(self.client.login(
            username=self.user.username,
            password=self.password
        ))
        resp = self.client.get(self.project.get_absolute_url(), follow=True)
        self.assertNotContains(resp, self.project.get_edit_url())
        self.assertTrue(self.client.login(
            username=self.owner.username,
            password=self.owner_password
        ))
        resp = self.client.get(self.project.get_absolute_url(), follow=True)
        self.assertContains(resp, self.project.get_edit_url())

    def test_only_owner_can_see_edit_page(self):
        """Test that only a project owner can get the edit page"""
        # unauthenticated user should go home
        resp = self.client.get(self.project.get_edit_url(), follow=True)
        furl, fcode = resp.redirect_chain[-1]
        self.assertTrue(furl.startswith('http://testserver/en-US/?next='))
        # normal user should go back to project
        self.assertTrue(self.client.login(
            username=self.user.username,
            password=self.password
        ))
        resp = self.client.get(self.project.get_edit_url(), follow=True)
        furl, fcode = resp.redirect_chain[-1]
        self.assertTrue(furl.endswith(self.project.get_absolute_url()))
        self.assertEqual(resp.status_code, 200)
        # owner should stay
        self.assertTrue(self.client.login(
            username=self.owner.username,
            password=self.owner_password
        ))
        resp = self.client.get(self.project.get_edit_url(), follow=True)
        furl, fcode = resp.redirect_chain[-1]
        self.assertTrue(furl.endswith(self.project.get_edit_url()))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Edit Project')

    def test_owner_can_update_project(self):
        """Test that a project owner can update his project"""
        self.assertTrue(self.client.login(
            username=self.owner.username,
            password=self.owner_password
        ))
        new_name = 'Rug Acquisition Committee'
        new_desc = 'And he is still not into the whole, brevity thing'
        # TODO: make localized URL handling suck less
        self.client.post('/en-US' + self.project.get_edit_url(), {
            'name': new_name,
            'slug': 'rug-back',
            'description': 'All The Dude ever wanted... was his rug back.',
            'long_description': new_desc,
            'topics': [self.topic.id],
            'team_members_1': [self.profile.pk],
            'owners_1': [self.owner_profile.pk],
        })
        proj = Project.objects.get(pk=self.project.pk)
        self.assertEqual(proj.name, new_name)
        self.assertEqual(proj.long_description, new_desc)

    def test_updating_project_members(self):
        """Test that updating project members works."""
        self.assertTrue(self.client.login(
            username=self.owner.username,
            password=self.owner_password
        ))
        self.assertFalse(self.owner_profile in self.project.team_members.all())
        # warm cache
        self.client.get('/en-US' + self.project.get_absolute_url())
        self.client.get('/en-US' + self.project.get_edit_url())
        self.client.post('/en-US' + self.project.get_edit_url(), {
            'name': self.project.name,
            'slug': self.project.slug,
            'description': self.project.description,
            'long_description': self.project.long_description,
            'topics': [self.topic.id],
            'team_members_1': [self.profile.pk, self.owner_profile.pk],
            'owners_1': [self.owner_profile.pk],
            })
        self.assertTrue(self.owner_profile in self.project.team_members.all())
        self.assertTrue(self.profile in self.project.team_members.all())

    def test_owner_cannot_inject_xss(self):
        """Test that a user cannot inject xss into fields marked safe."""
        self.assertTrue(self.client.login(
            username=self.user.username,
            password=self.password
        ))
        self.client.post('/en-US' + self.project_xss.get_edit_url(), {
            'topics': [self.topic.id],
            'team_members': [self.profile.pk],
            'owners_1': [self.owner_profile.pk],
        })
        proj = Project.objects.get(pk=self.project_xss.pk)
        self.assertEqual(proj.long_description, "alert('i am evil');")

    def test_non_owner_cannot_update_project(self):
        """Test that a normal user cannot update a project"""
        self.assertTrue(self.client.login(
            username=self.user.username,
            password=self.password
        ))
        new_name = 'Rug Acquisition Committee'
        new_desc = 'And he is still not into the whole, brevity thing'
        # TODO: make localized URL handling suck less
        self.client.post('/en-US' + self.project.get_edit_url(), {
            'name': new_name,
            'slug': 'rug-back',
            'description': 'All The Dude ever wanted... was his rug back.',
            'long_description': new_desc,
            'topics': [self.topic.id],
            'team_members_1': [self.profile.pk],
            'owners_1': [self.owner_profile.pk],
            })
        proj = Project.objects.get(pk=self.project.pk)
        self.assertEqual(proj.name, self.project.name)
        self.assertEqual(proj.long_description, self.project.long_description)

    def test_owner_can_delete_project_links(self):
        """Test that a project owner can delete links"""
        self.assertTrue(self.client.login(
            username=self.owner.username,
            password=self.owner_password
        ))
        link = Link.objects.create(
            project=self.project,
            name='Testing',
            url='http://example.com',
        )
        resp = self.client.post(reverse('projects_links_delete',
            kwargs={'pk': link.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp.status_code, 204)
        with self.assertRaises(Link.DoesNotExist):
            Link.objects.get(pk=link.pk)

    def test_non_owner_cannot_delete_project_links(self):
        """Test that only the project owner can delete links"""
        self.assertTrue(self.client.login(
            username=self.user.username,
            password=self.password
        ))
        link = Link.objects.create(
            project=self.project,
            name='Testing',
            url='http://example.com',
        )
        resp = self.client.post(reverse('projects_links_delete',
            kwargs={'pk': link.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp.status_code, 403)
        resp = self.client.get(self.project.get_absolute_url(), follow=True)
        self.assertContains(resp, link.url)

    def test_can_list_project_links(self):
        """Make sure the project links list ajax view works"""
        self.assertTrue(self.client.login(
            username=self.user.username,
            password=self.password
        ))
        link = Link.objects.create(
            project=self.project,
            name='Testing',
            url='http://example.com',
        )
        resp = self.client.get(reverse(
            'projects_links_list',
            kwargs={'slug': self.project.slug},
        ), follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(resp, link.url)

    def test_cannot_list_project_links_without_ajax(self):
        """Test that the project links list view is ajax only"""
        self.assertTrue(self.client.login(
            username=self.user.username,
            password=self.password
        ))
        Link.objects.create(
            project=self.project,
            name='Testing',
            url='http://example.com',
        )
        resp = self.client.get(reverse(
            'projects_links_list',
            kwargs={'slug': self.project.slug},
        ), follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_owner_can_add_links(self):
        """Test that an owner can add links to his project"""
        self.assertTrue(self.client.login(
            username=self.owner.username,
            password=self.owner_password
        ))
        link_url = 'http://eldudarino.com/2012/03/12/donnie-wasnt-listening'
        self.client.post(reverse(
            'projects_links_add',
            kwargs={'slug': self.project.slug},
        ), {
            'name': "The Dude's Story",
            'url': link_url,
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        resp = self.client.get(reverse(
            'projects_links_list',
            kwargs={'slug': self.project.slug},
        ), follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(resp, link_url)

    def test_owner_cannot_add_links_without_ajax(self):
        """Test that no one can post to the addlink url without ajax"""
        self.assertTrue(self.client.login(
            username=self.owner.username,
            password=self.owner_password
        ))
        link_url = 'http://eldudarino.com/2012/03/12/donnie-wasnt-listening'
        self.client.post(reverse(
            'projects_links_add',
            kwargs={'slug': self.project.slug},
        ), {
            'name': "The Dude's Story",
            'url': link_url,
        })
        resp = self.client.get(reverse(
            'projects_links_list',
            kwargs={'slug': self.project.slug},
        ), follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotContains(resp, link_url)
