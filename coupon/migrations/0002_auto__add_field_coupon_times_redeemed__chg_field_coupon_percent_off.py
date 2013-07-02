# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Coupon.times_redeemed'
        db.add_column('coupon_coupon', 'times_redeemed',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


        # Changing field 'Coupon.percent_off'
        db.alter_column('coupon_coupon', 'percent_off', self.gf('django.db.models.fields.IntegerField')())

    def backwards(self, orm):
        # Deleting field 'Coupon.times_redeemed'
        db.delete_column('coupon_coupon', 'times_redeemed')


        # Changing field 'Coupon.percent_off'
        db.alter_column('coupon_coupon', 'percent_off', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2))

    models = {
        'coupon.coupon': {
            'Meta': {'object_name': 'Coupon'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'amount_off': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'applies_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Product']", 'symmetrical': 'False'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_redemptions': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'percent_off': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'redeem_by': ('django.db.models.fields.DateField', [], {}),
            'repeat_duration': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'times_redeemed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'main.product': {
            'Meta': {'object_name': 'Product'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'cart_tag': ('django.db.models.fields.CharField', [], {'default': "'x'", 'max_length': '64'}),
            'category': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'full_case_price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '10', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'sku': ('django.db.models.fields.CharField', [], {'default': "'xxxxxxxxxxxxxxxxxxxxxxxxxx'", 'max_length': '32'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'unit_price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '10', 'decimal_places': '2'})
        }
    }

    complete_apps = ['coupon']