# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Venue'
        db.delete_table('events_venue')

        # Deleting model 'Event'
        db.delete_table('events_event')

        # Removing M2M table for field attendees on 'Event'
        db.delete_table('events_event_attendees')


    def backwards(self, orm):
        
        # Adding model 'Venue'
        db.create_table('events_venue', (
            ('address_two', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=15, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, unique=True, db_index=True)),
        ))
        db.send_create_signal('events', ['Venue'])

        # Adding model 'Event'
        db.create_table('events_event', (
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('featured_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, unique=True, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('venue', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['events.Venue'], null=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='events', null=True, to=orm['users.Profile'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('events', ['Event'])

        # Adding M2M table for field attendees on 'Event'
        db.create_table('events_event_attendees', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm['events.event'], null=False)),
            ('profile', models.ForeignKey(orm['users.profile'], null=False))
        ))
        db.create_unique('events_event_attendees', ['event_id', 'profile_id'])


    models = {
        
    }

    complete_apps = ['events']
