from django.contrib import admin

from tower import ugettext_lazy as _

from users.models import Profile, Link


username = lambda u: u.user.username
username.short_description = _('Username')


class ProfileAdmin(admin.ModelAdmin):
    list_display = (username, 'name')
    search_fields = ('name',)


class LinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    search_fields = ('name', 'url')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Link, LinkAdmin)
