import urllib

import jingo


@jingo.register.filter
def urlquote(s):
    return urllib.quote(s)
