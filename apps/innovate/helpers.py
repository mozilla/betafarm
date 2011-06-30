from jingo import register


@register.function
def active(request, url):
    if request.path.startswith(url):
        return ' selected'
