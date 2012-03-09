# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Activity'
        db.delete_table('activity_activity')


    def backwards(self, orm):
        
        # Adding model 'Activity'
        db.create_table('activity_activity', (
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['feeds.Entry'], unique=True, null=True, blank=True)),
            ('published_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('activity', ['Activity'])


    models = {
        
    }

    complete_apps = ['activity']
