import bleach
import feedparser
import urllib2

from django.core.management.base import BaseCommand

from feeds.models import Entry
from projects.models import Project
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
        ./manage.py importfeed http://feed/url project-slug 10
        """
        if len(args) < 2:
            print 'You must provide a feed URL and a project slug'
            print 'usage: ./manage.py feedurl project-slug [nentries]'
            return
        (feed_url, slug) = args[:2]
        try:
            project = Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            print 'Unknown project: %s' % (slug,)
            return
        feed = urllib2.urlopen(feed_url).read()
        parsed = feedparser.parse(feed)
        for entry in parsed.entries:
            parsed_entry = FeedEntryParser(entry)
            content = bleach.clean(
                parsed_entry.content, tags=TAGS, attributes=ATTRIBUTES,
                strip=True)
            entry = Entry.objects.create(
                title=parsed_entry.title, link=parsed_entry.link, body=content,
                project=project, published=parsed_entry.updated)
            print entry
