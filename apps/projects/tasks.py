from celery.task import Task
from django_push.subscriber.models import Subscription

from projects.utils import PushFeedParser
from feeds.models import Entry


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
            projects = filter(lambda x: x not in ['', None],
                              [link.project for link in sender.link_set.all()])
            for project in projects:
                entry = Entry(title=title, link=link,
                              body=content, project=project)
                entry.save()
