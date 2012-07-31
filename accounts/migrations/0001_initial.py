# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Address'
        db.create_table('accounts_address', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nick_name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('company_co', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('street1', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('street2', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('state', self.gf('django.contrib.localflavor.us.models.USStateField')(max_length=2)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('accounts', ['Address'])

        # Adding model 'CreditCard'
        db.create_table('accounts_creditcard', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nick_name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('card_number', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('exp_month', self.gf('django.db.models.fields.IntegerField')()),
            ('exp_year', self.gf('django.db.models.fields.IntegerField')()),
            ('verification_code', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('billing_zipcode', self.gf('django.db.models.fields.CharField')(max_length=5)),
        ))
        db.send_create_signal('accounts', ['CreditCard'])

        # Adding model 'VerificationQueue'
        db.create_table('accounts_verificationqueue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('verification_code', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('accounts', ['VerificationQueue'])

        # Adding model 'UserProfile'
        db.create_table('accounts_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('dob', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('dl_number', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('accepted_tos', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('news_optin', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('age', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('above_21', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('wine_personality', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personality.WinePersonality'], null=True, blank=True)),
            ('prequestionnaire', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('billing_address', self.gf('django.db.models.fields.related.ForeignKey')(related_name='billed_to', null=True, to=orm['accounts.Address'])),
            ('shipping_address', self.gf('django.db.models.fields.related.ForeignKey')(related_name='shipped_to', null=True, to=orm['accounts.Address'])),
            ('credit_card', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owner', null=True, to=orm['accounts.CreditCard'])),
        ))
        db.send_create_signal('accounts', ['UserProfile'])

        # Adding M2M table for field credit_cards on 'UserProfile'
        db.create_table('accounts_userprofile_credit_cards', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['accounts.userprofile'], null=False)),
            ('creditcard', models.ForeignKey(orm['accounts.creditcard'], null=False))
        ))
        db.create_unique('accounts_userprofile_credit_cards', ['userprofile_id', 'creditcard_id'])

        # Adding M2M table for field party_addresses on 'UserProfile'
        db.create_table('accounts_userprofile_party_addresses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['accounts.userprofile'], null=False)),
            ('address', models.ForeignKey(orm['accounts.address'], null=False))
        ))
        db.create_unique('accounts_userprofile_party_addresses', ['userprofile_id', 'address_id'])

        # Adding M2M table for field shipping_addresses on 'UserProfile'
        db.create_table('accounts_userprofile_shipping_addresses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['accounts.userprofile'], null=False)),
            ('address', models.ForeignKey(orm['accounts.address'], null=False))
        ))
        db.create_unique('accounts_userprofile_shipping_addresses', ['userprofile_id', 'address_id'])


    def backwards(self, orm):
        # Deleting model 'Address'
        db.delete_table('accounts_address')

        # Deleting model 'CreditCard'
        db.delete_table('accounts_creditcard')

        # Deleting model 'VerificationQueue'
        db.delete_table('accounts_verificationqueue')

        # Deleting model 'UserProfile'
        db.delete_table('accounts_userprofile')

        # Removing M2M table for field credit_cards on 'UserProfile'
        db.delete_table('accounts_userprofile_credit_cards')

        # Removing M2M table for field party_addresses on 'UserProfile'
        db.delete_table('accounts_userprofile_party_addresses')

        # Removing M2M table for field shipping_addresses on 'UserProfile'
        db.delete_table('accounts_userprofile_shipping_addresses')


    models = {
        'accounts.address': {
            'Meta': {'object_name': 'Address'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'company_co': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nick_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2'}),
            'street1': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'street2': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'accounts.creditcard': {
            'Meta': {'object_name': 'CreditCard'},
            'billing_zipcode': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'card_number': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'exp_month': ('django.db.models.fields.IntegerField', [], {}),
            'exp_year': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nick_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'verification_code': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        'accounts.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'above_21': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'accepted_tos': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'age': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'billing_address': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'billed_to'", 'null': 'True', 'to': "orm['accounts.Address']"}),
            'credit_card': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'null': 'True', 'to': "orm['accounts.CreditCard']"}),
            'credit_cards': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'owned_by'", 'symmetrical': 'False', 'to': "orm['accounts.CreditCard']"}),
            'dl_number': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'news_optin': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'party_addresses': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'hosting_user'", 'symmetrical': 'False', 'to': "orm['accounts.Address']"}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'prequestionnaire': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shipping_address': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shipped_to'", 'null': 'True', 'to': "orm['accounts.Address']"}),
            'shipping_addresses': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'shipping_user'", 'symmetrical': 'False', 'to': "orm['accounts.Address']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'wine_personality': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personality.WinePersonality']", 'null': 'True', 'blank': 'True'})
        },
        'accounts.verificationqueue': {
            'Meta': {'object_name': 'VerificationQueue'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'verification_code': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'personality.winepersonality': {
            'Meta': {'object_name': 'WinePersonality'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['accounts']