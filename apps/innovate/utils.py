import bleach
import feedparser
import hashlib
import math
import os
import logging
import time

from PIL import Image

from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage

from projects.utils import FeedEntryParser


logger = logging.getLogger(__name__)


BLOG_FEED_URL = getattr(settings, 'BLOG_FEED_URL', None)
BLOG_FEED_NUM_ENTRIES = getattr(settings, 'BLOG_FEED_NUM_ENTRIES', 5)
BLOG_FEED_CACHE_KEY = 'labs_blog_feed_entries'
# hours
BLOG_FEED_CACHE_FOR = getattr(settings, 'BLOG_FEED_CACHE_FOR', 5) * 3600
# Whitelisted tags and attributes
TAGS = (
    'h1', 'h2', 'h3', 'h4', 'h5', 'a', 'b', 'em',
    'i', 'strong', 'ol', 'ul', 'li', 'hr', 'blockquote',
    'p', 'span', 'pre', 'code', 'img',
)
ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt'],
}
IMAGE_WIDTH = 140
IMAGE_HEIGHT = 140


def get_blog_feed_entries(force_update=False):
    """Gets posts from the configured blog feed and caches them."""
    entries = cache.get(BLOG_FEED_CACHE_KEY, [])
    if force_update or not entries:
        entries = _get_blog_entries_nocache()
        if entries:
            cache.set(BLOG_FEED_CACHE_KEY, entries, BLOG_FEED_CACHE_FOR)
    return entries


def _get_blog_entries_nocache():
    """Does the real work of getting the posts from the blog."""
    entries = []
    if BLOG_FEED_URL:
        parsed = feedparser.parse(BLOG_FEED_URL)
        for entry in parsed.entries:
            if len(entries) == BLOG_FEED_NUM_ENTRIES:
                break
            summary = getattr(entry, 'summary', None)
            parsed_entry = FeedEntryParser(entry)
            content = bleach.clean(summary or parsed_entry.content,
                                   tags=TAGS,
                                   attributes=ATTRIBUTES,
                                   strip=True)
            entries.append({
                'title': parsed_entry.title,
                'url': parsed_entry.link,
                'body': content,
                'published': parsed_entry.updated,
                'is_summary': bool(summary),
            })
    return entries


def get_partition_id(pk, chunk_size=1000):
    """
    Given a primary key and optionally the number of models that will get
    shared access to a directory, return an integer representing a directory
    name.
    """
    return int(math.ceil(pk / float(chunk_size)))


def safe_filename(filename):
    """Generate a safe filename for storage."""
    name, ext = os.path.splitext(filename)
    return "%s%s" % (hashlib.md5(name.encode('utf8')).hexdigest(), ext)


class ImageStorage(FileSystemStorage):
    """Image resizing functionality."""
    format_extensions = {
        'PNG': 'png',
        'GIF': 'gif',
        'JPEG': 'jpg',
        'JPG': 'jpg',
    }

    def _save(self, name, content):
        name, ext = os.path.splitext(name)
        image = Image.open(content)
        if image.format not in self.format_extensions:
            raise Exception("Unknown image format: %s" % (image.format,))
        format = self.format_extensions[image.format]
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')
        image.thumbnail((IMAGE_WIDTH, IMAGE_HEIGHT), Image.ANTIALIAS)
        name = "%s%s.%s" % (name, str(time.time()), format)
        image.save(self.path(name), image.format)
        return name


def thumbnailify_image(field):
    """Resize an image from an ImageField to a max height and width"""
    if field and (field.height > IMAGE_HEIGHT or field.width > IMAGE_WIDTH):
        logger.debug('Resizing image: %s', field.name)
        img = Image.open(field.path)
        img.thumbnail((IMAGE_WIDTH, IMAGE_HEIGHT), Image.ANTIALIAS)
        img.save(field.path)
