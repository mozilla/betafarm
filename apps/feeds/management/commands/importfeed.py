import bleach
import feedparser
import urllib2

from django.core.management.base import BaseCommand

from feeds.models import Entry
from projects.models import Link
from projects.utils import FeedEntryParser

# Whitelisted tags and attributes
TAGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'a', 'b', 'em',
        'i', 'strong', 'ol', 'ul', 'li', 'hr', 'blockquote',
        'p', 'span', 'pre', 'code', 'img')

ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt']
}


class Command(BaseCommand):
    help = u'Import entries from an RSS or Atom feed.'

    def handle(self, *args, **options):
        """
        ./manage.py importfeed http://feed/url linkid 10
        """
        if len(args) < 2:
            print 'You must provide a feed URL and a link id'
            print 'usage: ./manage.py feedurl linkid [nentries]'
            return
        (feed_url, link_id) = args[:2]
        try:
            link = Link.objects.get(id=link_id)
        except Link.DoesNotExist:
            print 'No link with id: %d' % (link_id,)
            return
        feed = urllib2.urlopen(feed_url).read()
        parsed = feedparser.parse(feed)
        for entry in parsed.entries:
            parsed_entry = FeedEntryParser(entry)
            content = bleach.clean(
                parsed_entry.content, tags=TAGS, attributes=ATTRIBUTES,
                strip=True)
            entry = Entry.objects.create(
                title=parsed_entry.title, url=parsed_entry.link, body=content,
                link=link, published=parsed_entry.updated)
            print entry
