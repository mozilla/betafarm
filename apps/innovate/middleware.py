from django.contrib import messages
from django.core.urlresolvers import reverse, resolve
from django.http import HttpResponseRedirect

from tower import ugettext as _


class ProfileMiddleware(object):
    def process_request(self, request):
        try:
            path = u'/%s' % ('/'.join(request.path.split('/')[2:]),)
            match = resolve(path)
            if match.url_name in ('users_edit', 'django.views.static.serve'):
                return
        except:
            return
        if request.user.is_authenticated():
            profile = request.user.get_profile()
            if profile.display_name == profile.masked_email:
                msg = _('''<strong>Almost done!</strong>
                Just fill in a bit of profile information and
                you\'ll be all set. At a minimum you\'ll need
                to enter a display name so we know what to call
                you.''')
                messages.success(request, msg)
                return HttpResponseRedirect(reverse('users_edit'))
