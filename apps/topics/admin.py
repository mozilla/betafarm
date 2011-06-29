from django.contrib import admin

from topics.models import Topic


class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

admin.site.register(Topic, TopicAdmin)
