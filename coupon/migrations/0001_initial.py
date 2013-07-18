# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Coupon'
        db.create_table('coupon_coupon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=24)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('repeat_duration', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('amount_off', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('percent_off', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=5, decimal_places=2)),
            ('max_redemptions', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('redeem_by', self.gf('django.db.models.fields.DateField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('coupon', ['Coupon'])

        # Adding M2M table for field applies_to on 'Coupon'
        db.create_table('coupon_coupon_applies_to', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('coupon', models.ForeignKey(orm['coupon.coupon'], null=False)),
            ('product', models.ForeignKey(orm['main.product'], null=False))
        ))
        db.create_unique('coupon_coupon_applies_to', ['coupon_id', 'product_id'])


    def backwards(self, orm):
        # Deleting model 'Coupon'
        db.delete_table('coupon_coupon')

        # Removing M2M table for field applies_to on 'Coupon'
        db.delete_table('coupon_coupon_applies_to')


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
            'max_redemptions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'percent_off': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2'}),
            'redeem_by': ('django.db.models.fields.DateField', [], {}),
            'repeat_duration': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'main.product': {
            'Meta': {'object_name': 'Product'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'cart_tag': ('django.db.models.fields.CharField', [], {'default': "'x'", 'max_length': '64'}),
            'category': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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