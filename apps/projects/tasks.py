from celery.task import Task
from django_push.subscriber.models import Subscription, SubscriptionError

from projects.utils import PushFeedParser
from feeds.models import Entry


class PushSubscriber(Task):

    def run(self, link, **kwargs):
        log = self.get_logger(**kwargs)
        p = PushFeedParser(link.url)
        p.parse()
        try:
            link.subscription = Subscription.objects.subscribe(
                p.feed_url, hub=p.hub_url)
            link.save()
        except SubscriptionError, e:
            log.warning('SubscriptionError. Retrying (%s)' % (link.url,))
            log.warning('Error: %s' % (str(e),))


class PushUnsubscriber(Task):

    def run(self, link, **kwargs):
        log = self.get_logger(**kwargs)
        if not link.subscription:
            log.warning(
                'Attempt to unsubscribe from link with no subscription: %s' % (
                    link.url,))
            return
        Subscription.objects.unsubscribe(link.url, hub=link.subscription.hub)


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
