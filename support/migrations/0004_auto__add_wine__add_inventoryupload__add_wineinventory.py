# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Wine'
        db.create_table('support_wine', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('year', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('sku', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('vinely_category', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('sparkling', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('color', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('support', ['Wine'])

        # Adding model 'InventoryUpload'
        db.create_table('support_inventoryupload', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('inventory_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('support', ['InventoryUpload'])

        # Adding model 'WineInventory'
        db.create_table('support_wineinventory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('wine', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['support.Wine'])),
            ('on_hand', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('support', ['WineInventory'])


    def backwards(self, orm):
        # Deleting model 'Wine'
        db.delete_table('support_wine')

        # Deleting model 'InventoryUpload'
        db.delete_table('support_inventoryupload')

        # Deleting model 'WineInventory'
        db.delete_table('support_wineinventory')


    models = {
        'support.email': {
            'Meta': {'object_name': 'Email'},
            'html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipients': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'support.inventoryupload': {
            'Meta': {'object_name': 'InventoryUpload'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inventory_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'support.wine': {
            'Meta': {'object_name': 'Wine'},
            'color': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'sparkling': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'vinely_category': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'year': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'support.wineinventory': {
            'Meta': {'object_name': 'WineInventory'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'on_hand': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'wine': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['support.Wine']"})
        }
    }

    complete_apps = ['support']