from django import forms

import jinja2
from tower import ugettext as _, ugettext_lazy as _l

from users.models import Profile, Link
from users.widgets import ImageFileInput


class ProfileForm(forms.ModelForm):

    avatar = forms.ImageField(
        widget=ImageFileInput(), required=False)
    name = forms.CharField(required=True, error_messages={
        'required': _l(u'A Display Name is required.')
    })

    class Meta:
        model = Profile
        fields = ('name', 'website', 'avatar', 'bio')


class ProfileCreateForm(ProfileForm):
    agreement = forms.BooleanField(required=True, error_messages={
        'required': _l(u'You must agree to the privacy policy to register.')
    })

    def __init__(self, *args, **kwargs):
        super(ProfileCreateForm, self).__init__(*args, **kwargs)

        self.fields['agreement'].label = jinja2.Markup(_(
            u"I'm okay with Mozilla handling this info as you explain in your "
            u"<a href='{url}' target='_blank'>privacy policy</a>.")).format(
                url='http://www.mozilla.org/en-US/privacy-policy.html')


class ProfileLinksForm(forms.ModelForm):

    class Meta:
        model = Link
        fields = ('name', 'url')
