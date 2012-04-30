# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Entry'
        db.delete_table('feeds_entry')


    def backwards(self, orm):
        
        # Adding model 'Entry'
        db.create_table('feeds_entry', (
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('link', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Link'])),
            ('published', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 8, 15, 10, 57, 47, 723986))),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('feeds', ['Entry'])


    models = {
        
    }

    complete_apps = ['feeds']
