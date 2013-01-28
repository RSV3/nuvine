# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Wine.vinely_category2'
        db.add_column('support_wine', 'vinely_category2',
                      self.gf('django.db.models.fields.FloatField')(default=1.0),
                      keep_default=False)

        # Adding field 'Wine.vintage'
        db.add_column('support_wine', 'vintage',
                      self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Wine.varietal'
        db.add_column('support_wine', 'varietal',
                      self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Wine.region'
        db.add_column('support_wine', 'region',
                      self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Wine.alcohol'
        db.add_column('support_wine', 'alcohol',
                      self.gf('django.db.models.fields.FloatField')(default=0.0),
                      keep_default=False)

        # Adding field 'Wine.residual_sugar'
        db.add_column('support_wine', 'residual_sugar',
                      self.gf('django.db.models.fields.FloatField')(default=0.0),
                      keep_default=False)

        # Adding field 'Wine.acidity'
        db.add_column('support_wine', 'acidity',
                      self.gf('django.db.models.fields.FloatField')(default=0.0),
                      keep_default=False)

        # Adding field 'Wine.ph'
        db.add_column('support_wine', 'ph',
                      self.gf('django.db.models.fields.FloatField')(default=0.0),
                      keep_default=False)

        # Adding field 'Wine.oak'
        db.add_column('support_wine', 'oak',
                      self.gf('django.db.models.fields.FloatField')(default=0.0),
                      keep_default=False)

        # Adding field 'Wine.body'
        db.add_column('support_wine', 'body',
                      self.gf('django.db.models.fields.FloatField')(default=0.0),
                      keep_default=False)

        # Adding field 'Wine.fruit'
        db.add_column('support_wine', 'fruit',
                      self.gf('django.db.models.fields.FloatField')(default=0.0),
                      keep_default=False)

        # Adding field 'Wine.tannin'
        db.add_column('support_wine', 'tannin',
                      self.gf('django.db.models.fields.FloatField')(default=0.0),
                      keep_default=False)

        # Adding field 'Wine.supplier'
        db.add_column('support_wine', 'supplier',
                      self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Wine.vinely_category2'
        db.delete_column('support_wine', 'vinely_category2')

        # Deleting field 'Wine.vintage'
        db.delete_column('support_wine', 'vintage')

        # Deleting field 'Wine.varietal'
        db.delete_column('support_wine', 'varietal')

        # Deleting field 'Wine.region'
        db.delete_column('support_wine', 'region')

        # Deleting field 'Wine.alcohol'
        db.delete_column('support_wine', 'alcohol')

        # Deleting field 'Wine.residual_sugar'
        db.delete_column('support_wine', 'residual_sugar')

        # Deleting field 'Wine.acidity'
        db.delete_column('support_wine', 'acidity')

        # Deleting field 'Wine.ph'
        db.delete_column('support_wine', 'ph')

        # Deleting field 'Wine.oak'
        db.delete_column('support_wine', 'oak')

        # Deleting field 'Wine.body'
        db.delete_column('support_wine', 'body')

        # Deleting field 'Wine.fruit'
        db.delete_column('support_wine', 'fruit')

        # Deleting field 'Wine.tannin'
        db.delete_column('support_wine', 'tannin')

        # Deleting field 'Wine.supplier'
        db.delete_column('support_wine', 'supplier')


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
            'wine': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['support.Wine']"})
        }
    }

    complete_apps = ['support']