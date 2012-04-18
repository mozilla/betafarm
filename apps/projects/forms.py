from __future__ import absolute_import

from django import forms

from selectable.forms import AutoCompleteSelectMultipleField

from .models import Project, Link
from users.lookups import ProfileLookup


class ProjectForm(forms.ModelForm):
    owners = AutoCompleteSelectMultipleField(ProfileLookup)
    team_members = AutoCompleteSelectMultipleField(ProfileLookup)

    class Meta:
        model = Project
        fields = (
            'name',
            'slug',
            'description',
            'long_description',
            'image',
            'featured_image',
            'owners',
            'team_members',
            'topics',
            'tags',
            'inactive',
        )


class LinkForm(forms.ModelForm):

    class Meta:
        model = Link
        fields = ('name', 'url', 'blog')
