# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StripeCard'
        db.create_table('stripecard_stripecard', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stripe_user', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('exp_month', self.gf('django.db.models.fields.IntegerField')()),
            ('exp_year', self.gf('django.db.models.fields.IntegerField')()),
            ('card_type', self.gf('django.db.models.fields.CharField')(default='Unknown', max_length=10)),
            ('last_four', self.gf('django.db.models.fields.CharField')(max_length=4)),
        ))
        db.send_create_signal('stripecard', ['StripeCard'])


    def backwards(self, orm):
        # Deleting model 'StripeCard'
        db.delete_table('stripecard_stripecard')


    models = {
        'stripecard.stripecard': {
            'Meta': {'object_name': 'StripeCard'},
            'card_type': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '10'}),
            'exp_month': ('django.db.models.fields.IntegerField', [], {}),
            'exp_year': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_four': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'stripe_user': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['stripecard']