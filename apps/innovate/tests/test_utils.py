from mock import Mock, patch
from os import path

from django.test import Client, TestCase

import innovate.utils
from innovate.tests import _save_image
from innovate.utils import ImageStorage


def test_get_blog_entries():
    """Get the latest blog entries."""
    innovate.utils.BLOG_FEED_URL = path.join(
        path.dirname(path.abspath(__file__)),
        'feed.rss'
    )
    innovate.utils.cache.clear()
    entries = innovate.utils.get_blog_feed_entries()
    assert len(entries) == innovate.utils.BLOG_FEED_NUM_ENTRIES, len(entries)
    titles = [
        'Scrum and Bugzilla - TEST', # make sure it's using the file
        'Rapid Prototyping',
        'Better Know a WebDev: Luke Crouch (aka groovecoder)',
        'Better Know a WebDev: Kumar McMillan (aka kumar303)',
        'Better Know a WebDev: Greg Koberger aka gkoberger',
    ]
    for i, entry in enumerate(entries):
        assert entry['title'] == titles[i], "%s != %s" % (entry['title'],
                                                          titles[i])
    client = Client()
    resp = client.get('/en-US/')
    for title in titles:
        assert title in resp.content, "%s not in content" % title


class UtilitiesData(TestCase):
    @patch('innovate.utils.Image')
    def test_file_upload_success(self, Image):
        mock_image = _save_image()

        self.assertEqual(mock_image.format, 'PNG')
        mock_image.resize.assert_called_with((140, 140), 1)


    def test_file_upload_failure(self):
        with self.assertRaises(Exception):
            _save_image(format='MP3')


    @patch('innovate.utils.Image')
    def test_file_valid_mode(self, Image):
        mock_image = _save_image(mode='ABC')

        mock_image.convert.assert_called_with('RGB')
