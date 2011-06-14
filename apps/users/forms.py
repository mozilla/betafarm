from django import forms
from django.contrib.auth import forms as auth_forms

from tower import ugettext_lazy as _lazy

from django.contrib.auth.models import User


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


class AuthenticationForm(auth_forms.AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput(render_value=False))
    remember_me = forms.BooleanField(required=False)
