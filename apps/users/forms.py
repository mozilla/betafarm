import re

from django import forms
from django.conf import settings
from django.contrib.auth import forms as auth_forms

from tower import ugettext as _, ugettext_lazy as _lazy

from django.contrib.auth.models import User


def check_password_complexity(password):
    if len(password) < 8 or not (
        re.search('[A-Za-z]', password) and re.search('[0-9]', password)):
        raise forms.ValidationError(_('Password must be at least 8 ' +
                                      'characters long and contain ' +
                                      'both numbers and letters.'))
    blacklisted = getattr(settings, 'PASSWORD_BLACKLIST', None)
    if blacklisted and password in blacklisted:
        raise forms.ValidationError(_('Password is too common. ' +
                                      'Please choose another.'))


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=255)
    email = forms.EmailField(label=_lazy(u'Email address:'))
    password = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(render_value=False))
    password_confirm = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = User
        fields = ('username', 'password', 'password_confirm', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'off'}),
        }

    def clean(self):
        super(self.__class__, self).clean()
        password = self.cleaned_data['password']
        password_confirm = self.cleaned_data['password_confirm']
        if not password == password_confirm:
            raise forms.ValidationError(_('Passwords do not match.'))
        check_password_complexity(password)
        return self.cleaned_data


class AuthenticationForm(auth_forms.AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput(render_value=False))
    remember_me = forms.BooleanField(required=False)
