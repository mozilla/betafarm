from django.contrib import messages
from django.core.urlresolvers import reverse, resolve
from django.http import HttpResponseRedirect

from tower import ugettext as _


class ProfileMiddleware(object):

    @classmethod
    def safe_paths(cls):
        return ('users_edit', 'django.views.static.serve', 'users_signout',
                'users_profile_add_link', 'users_profile_links',
                'users_profile_delete_link')

    def is_safe(self, path):
        try:
            match = resolve(path)
            return match.url_name in self.__class__.safe_paths()
        except:
            return False

    def process_request(self, request):
        # django debug_toolbar
        if '__debug__' in request.path:
            return
        if self.is_safe(request.path):
            return
        path = u'/%s' % ('/'.join(request.path.split('/')[2:]),)
        if self.is_safe(path):
            return
        if request.user.is_authenticated():
            profile = request.user.get_profile()
            if profile.has_chosen_identifier:
                return
            msg = _('''<strong>Almost done!</strong>
            Just fill in a bit of profile information and
            you\'ll be all set. At a minimum you\'ll need
            to enter a display name so we know what to call
            you.''')
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('users_edit'))
