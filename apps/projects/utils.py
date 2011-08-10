import feedparser
import time
import urllib2
import urlparse

from BeautifulSoup import BeautifulSoup

from django.conf import settings

DEFAULT_HUB_URL = getattr(settings, 'PUSH_DEFAULT_HUB', '')
test_attr = lambda a, v, o: a in o and o[a] == v


def normalize_url(url, base_url):
    """Try to detect relative URLs and convert them into absolute URLs."""
    parts = urlparse.urlparse(url)
    if parts.scheme and parts.netloc:
        return url  # looks fine
    if not base_url:
        return url
    base_parts = urlparse.urlparse(base_url)
    server = '://'.join((base_parts.scheme, base_parts.netloc))
    if server[-1] != '/' and url[0] != '/':
        server = server + '/'
    if server[-1] == '/' and url[0] == '/':
        server = server[:-1]
    return server + url


class FeedEntryParser(object):
    def __init__(self, entry):
        self.title = entry.title
        self.link = entry.link
        self.content = self._get_prefered_content(entry.content)
        self.updated = time.strftime('%Y-%m-%d %H:%M:%S',
                                     entry.updated_parsed)

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


class PushParsingError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class PushFeedParser(object):

    _test_attr = lambda self, attr, val, obj: obj.has_key(attr) and obj[attr] == val

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

    def get_feed_url(self, content):
        soup = BeautifulSoup(content)
        links = soup.findAll('link')
        feeds = filter(self._is_feed_test, links)
        return feeds[0].get('href', '')

    def get_hub_url(self, parsed):
        links = [l['href'] for l in parsed.feed.links
                 if self._is_hub_test(l)]
        if not links:
            self.hub_url = DEFAULT_HUB_URL
        else:
            self.hub_url = links[0]

    def parse(self):
        content = urllib2.urlopen(self.url).read()
        self.feed_url = normalize_url(self.get_feed_url(content), self.url)
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
