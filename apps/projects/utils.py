import feedparser

from django.conf import settings

DEFAULT_HUB_URL = getattr(settings, 'PUSH_DEFAULT_HUB', '')
test_attr = lambda a, v, o: a in o and o[a] == v


class PushParsingError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class PushFeedParser(object):

    _test_attr = lambda self, attr, val, obj: attr in obj and obj[attr] == val

    def __init__(self, url):
        self.url = url

    def _is_feed_test(self, link):
        def _rel_alternate_test(link):
            return self._test_attr('rel', 'alternate', link)

        def _rel_atom_test(link):
            return self._test_attr('type', 'application/atom+xml', link)

        def _rel_rss_test(link):
            return self._test_attr('type', 'application/rss+xml', link)

        return _rel_alternate_test(link) and (
            _rel_atom_test(link) or _rel_rss_test(link))

    def _is_hub_test(self, link):
        return self._test_attr('rel', 'hub', link)

    def get_feed_url(self, parsed):
        links = [l['href'] for l in parsed.feed.links
                 if self._is_feed_test(l)]
        if not links:
            raise PushParsingError('URL does not have an RSS/Atom feed')
        self.feed_url = links[0]

    def get_hub_url(self, parsed):
        links = [l['href'] for l in parsed.feed.links
                 if self._is_hub_test(l)]
        if not links:
            self.hub_url = DEFAULT_HUB_URL
        else:
            self.hub_url = links[0]

    def parse(self):
        parsed = feedparser.parse(self.url)
        if not parsed.feed:
            raise PushParsingError('URL does not have an RSS/Atom feed')
        self.get_feed_url(parsed)
        parsed_feed = feedparser.parse(self.feed_url)
        if not parsed_feed.feed:
            raise PushParsingError('Invalid Feed Format')
        self.get_hub_url(parsed_feed)


def push_hub_credentials(hub_url):
    """Credentials callback for django_push.subscribers."""
    if hub_url == DEFAULT_HUB_URL:
        username = getattr(settings, 'PUSH_DEFAULT_HUB_USERNAME', None)
        password = getattr(settings, 'PUSH_DEFAULT_HUB_PASSWORD', None)
        if not (username and password):
            return None
        return (username, password)
    return None
