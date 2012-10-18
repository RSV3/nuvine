# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'StripeCard.card_type'
        db.alter_column('stripecard_stripecard', 'card_type', self.gf('django.db.models.fields.CharField')(max_length=16))

    def backwards(self, orm):

        # Changing field 'StripeCard.card_type'
        db.alter_column('stripecard_stripecard', 'card_type', self.gf('django.db.models.fields.CharField')(max_length=10))

    models = {
        'stripecard.stripecard': {
            'Meta': {'object_name': 'StripeCard'},
            'card_type': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '16'}),
            'exp_month': ('django.db.models.fields.IntegerField', [], {}),
            'exp_year': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_four': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'stripe_user': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['stripecard']