from os import path

from django.test import Client

import innovate.utils


def test_get_blog_entries():
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

