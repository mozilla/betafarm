from django import forms

from users.models import Profile, Link
from users.widgets import ImageFileInput


class ProfileForm(forms.ModelForm):

    avatar = forms.ImageField(
        widget=ImageFileInput(), required=False)

    class Meta:
        model = Profile
        fields = ('name', 'website', 'avatar', 'bio')


class ProfileLinksForm(forms.ModelForm):

    class Meta:
        model = Link
        fields = ('name', 'url')
