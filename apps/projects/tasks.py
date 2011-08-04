import time
import bleach

from celery.task import Task
from django_push.subscriber.models import Subscription

from projects.utils import PushFeedParser
from feeds.models import Entry


# Whitelisted tags and attributes
TAGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'a', 'b', 'em',
        'i', 'strong', 'ol', 'ul', 'li', 'hr', 'blockquote',
        'p', 'span', 'pre', 'code', 'img')

ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt']
}


class PushSubscriber(Task):

    def run(self, link, **kwargs):
        p = PushFeedParser(link.url)
        p.parse()
        link.subscription = Subscription.objects.subscribe(
            p.feed_url, hub=p.hub_url)
        link.save()


class PushUnsubscriber(Task):

    def run(self, link, **kwargs):
        Subscription.objects.unsubscribe(link.url)


class PushNotificationHandler(Task):

    def _get_prefered_content(self, content):
        if not isinstance(content, list):
            return content.value
        for c in content:
            if c.type == 'text/html':
                return c.value
            if c.type == 'application/xhtml+xml':
                return c.value
            if c.type == 'text/plain':
                return c.value
        return content[0].value

    def create_entry(self, title, link, body, updated, project):
        body = bleach.clean(body, tags=TAGS, attributes=ATTRIBUTES)
        entry = Entry.objects.create(
            title=title, link=link, body=body, project=project,
            updated=updated)
        return entry

    def run(self, notification, sender, **kwargs):
        log = self.get_logger(**kwargs)
        if not isinstance(sender, Subscription):
            return
        for entry in notification.entries:
            log.debug('Received notification of entry: %s, %s' % (
                entry.title, entry.link))
            title = entry.title
            link = entry.link
            content = self._get_prefered_content(entry.content)
            updated = time.strftime('%Y-%m-%d %H:%M:%S', entry.updated_parsed)
            projects = filter(lambda x: x not in ['', None],
                              [link.project for link in sender.link_set.all()])
            for project in projects:
                self.create_entry(title, link, content, updated, project)
