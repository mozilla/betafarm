from django import forms

from users.models import Profile
from users.widgets import ImageFileInput


class ProfileForm(forms.ModelForm):

    avatar = forms.ImageField(
        widget=ImageFileInput(), required=False)

    class Meta:
        model = Profile
        fields = ('name', 'website', 'avatar', 'bio')
