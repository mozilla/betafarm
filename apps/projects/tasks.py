import bleach

from celery.task import Task
from django_push.subscriber.models import Subscription, SubscriptionError

from projects.utils import PushFeedParser, FeedEntryParser
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

    def create_entry(self, entry, link):
        content = bleach.clean(
            entry.content, tags=TAGS, attributes=ATTRIBUTES, strip=True)
        entry = Entry.objects.create(
            title=entry.title, url=entry.link, body=content,
            link=link, published=entry.updated)
        return entry

    def run(self, notification, sender, **kwargs):
        log = self.get_logger(**kwargs)
        if not isinstance(sender, Subscription):
            return
        for entry in notification.entries:
            log.debug('Received notification of entry: %s, %s' % (
                entry.title, entry.url))
            parsed = FeedEntryParser(entry)
            for link in sender.link_set.all():
                self.create_entry(parsed, link)
