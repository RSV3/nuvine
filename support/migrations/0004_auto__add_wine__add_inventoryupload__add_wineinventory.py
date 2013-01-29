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
            ('vinely_category2', self.gf('django.db.models.fields.FloatField')(default=1.0)),
            ('vintage', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('varietal', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('region', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('alcohol', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('residual_sugar', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('acidity', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('ph', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('oak', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('body', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('fruit', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('tannin', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('supplier', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('sparkling', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('color', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=7, decimal_places=2)),
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
            ('wine', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['support.Wine'], unique=True)),
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
            'acidity': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'alcohol': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'body': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'color': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fruit': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'oak': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'ph': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'residual_sugar': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'sparkling': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'supplier': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'tannin': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'varietal': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'vinely_category': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'vinely_category2': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'vintage': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'support.wineinventory': {
            'Meta': {'object_name': 'WineInventory'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'on_hand': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'wine': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['support.Wine']", 'unique': 'True'})
        }
    }

    complete_apps = ['support']