import cronjobs

from innovate.utils import get_blog_feed_entries


@cronjobs.register
def refresh_blog_feed():
    get_blog_feed_entries(force_update=True)
