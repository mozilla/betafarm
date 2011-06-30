from django.contrib import admin

from topics.models import Topic


class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Topic, TopicAdmin)
