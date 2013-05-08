# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from emailusernames.utils import create_user


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."
        profile = orm.Userprofile.objects.get(user__email='sales@vinely.com')
        sales_user = profile.user
        sales_user.first_name = "Vinely"
        sales_user.last_name = "Sales"
        sales_user.save()
        sales_user.userprofile.phone = '888-294-1128'
        sales_user.userprofile.save()

        care_user = create_user("care@vinely.com", "hello")
        care_user.first_name = "Vinely"
        care_user.last_name = "Care"
        care_user.is_active = False
        care_user.save()
        care_user.userprofile.role = 0  # no assigned role
        care_user.userprofile.phone = '888-294-1128'
        care_user.userprofile.save()

        pending_pro_profiles = orm.Userprofile.objects.filter(role=5, mentor__isnull=True)
        pending_pro_profiles.update(mentor=sales_user)

        host_profiles = orm.Userprofile.objects.filter(role=2, current_pro__isnull=True)
        host_profiles.update(current_pro=care_user)

    def backwards(self, orm):
        "Write your backwards methods here."
        profile = orm.Userprofile.objects.get(user__email='care@vinely.com')
        user = profile.user
        user.delete()

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
            'card_type': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '32'}),
            'exp_month': ('django.db.models.fields.IntegerField', [], {}),
            'exp_year': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nick_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'verification_code': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'accounts.subscriptioninfo': {
            'Meta': {'object_name': 'SubscriptionInfo'},
            'frequency': ('django.db.models.fields.IntegerField', [], {'default': '9'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'next_invoice_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'accounts.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'above_21': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'accepted_tos': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'billing_address': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billed_to'", 'null': 'True', 'to': "orm['accounts.Address']"}),
            'club_member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'credit_card': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owner'", 'null': 'True', 'to': "orm['accounts.CreditCard']"}),
            'credit_cards': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'owned_by'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['accounts.CreditCard']"}),
            'current_pro': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assigned_profiles'", 'null': 'True', 'to': "orm['auth.User']"}),
            'dl_number': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mentor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'mentor'", 'null': 'True', 'to': "orm['auth.User']"}),
            'news_optin': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'party_addresses': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'hosting_user'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['accounts.Address']"}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'prequestionnaire': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'role': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'shipping_address': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipped_to'", 'null': 'True', 'to': "orm['accounts.Address']"}),
            'shipping_addresses': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'shipping_user'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['accounts.Address']"}),
            'stripe_card': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'stripe_owner'", 'null': 'True', 'to': "orm['stripecard.StripeCard']"}),
            'stripe_cards': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'stripe_owned_by'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['stripecard.StripeCard']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'vinely_customer_id': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'wine_personality': ('django.db.models.fields.related.ForeignKey', [], {'default': '7', 'to': "orm['personality.WinePersonality']"}),
            'work_phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'accounts.verificationqueue': {
            'Meta': {'object_name': 'VerificationQueue'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'verification_code': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'verification_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'verify_data': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'accounts.vinelyproaccount': {
            'Meta': {'object_name': 'VinelyProAccount'},
            'account_number': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        },
        'accounts.zipcode': {
            'Meta': {'object_name': 'Zipcode'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'longitude': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'})
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
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'stripecard.stripecard': {
            'Meta': {'object_name': 'StripeCard'},
            'billing_zipcode': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'card_type': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '16'}),
            'exp_month': ('django.db.models.fields.IntegerField', [], {}),
            'exp_year': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_four': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'stripe_user': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['accounts']
    symmetrical = True
