from __future__ import absolute_import

from django import forms

from .models import Project, Link


class ProjectForm(forms.ModelForm):

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
            'tags'
        )


class LinkForm(forms.ModelForm):

    class Meta:
        model = Link
        fields = ('name', 'url', 'blog')
