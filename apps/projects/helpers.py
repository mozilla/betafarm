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
    'youtube'
)


@jingo.register.function
def favicon(url):
    cls = (u' %s' % (icon,) for icon in favicons if icon in url)
    try:
        return cls.next()
    except StopIteration:
        return u' default'
