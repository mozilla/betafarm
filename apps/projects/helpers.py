import jingo


favicons = (
    'flickr',
    'github',
    'facebook',
    'twitter',
    'blogger',
    'plus',
    'tumblr',
    'vimeo',
    'youtube',
    'addons',
    'rss',
    'atom',
    'feed',
)


@jingo.register.function
def favicon(url):
    cls = (u' icon-%s' % (icon,) for icon in favicons if icon in url)
    try:
        return cls.next()
    except StopIteration:
        return u' icon-link'
