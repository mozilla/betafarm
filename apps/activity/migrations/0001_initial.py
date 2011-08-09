# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Activity'
        db.create_table('activity_activity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_class', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('source_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('published_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('activity', ['Activity'])

        # Adding unique constraint on 'Activity', fields ['source_class', 'source_id']
        db.create_unique('activity_activity', ['source_class', 'source_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Activity', fields ['source_class', 'source_id']
        db.delete_unique('activity_activity', ['source_class', 'source_id'])

        # Deleting model 'Activity'
        db.delete_table('activity_activity')


    models = {
        'activity.activity': {
            'Meta': {'unique_together': "(('source_class', 'source_id'),)", 'object_name': 'Activity'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'published_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'source_class': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'source_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        }
    }

    complete_apps = ['activity']
