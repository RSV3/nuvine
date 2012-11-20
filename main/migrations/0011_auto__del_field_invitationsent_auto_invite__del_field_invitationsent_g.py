# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'InvitationSent.auto_invite'
        db.delete_column('main_invitationsent', 'auto_invite')

        # Deleting field 'InvitationSent.guests_can_invite'
        db.delete_column('main_invitationsent', 'guests_can_invite')

        # Deleting field 'InvitationSent.auto_thank_you'
        db.delete_column('main_invitationsent', 'auto_thank_you')

        # Adding field 'Party.auto_invite'
        db.add_column('main_party', 'auto_invite',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Party.auto_thank_you'
        db.add_column('main_party', 'auto_thank_you',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Party.guests_can_invite'
        db.add_column('main_party', 'guests_can_invite',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'InvitationSent.auto_invite'
        db.add_column('main_invitationsent', 'auto_invite',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'InvitationSent.guests_can_invite'
        db.add_column('main_invitationsent', 'guests_can_invite',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'InvitationSent.auto_thank_you'
        db.add_column('main_invitationsent', 'auto_thank_you',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'Party.auto_invite'
        db.delete_column('main_party', 'auto_invite')

        # Deleting field 'Party.auto_thank_you'
        db.delete_column('main_party', 'auto_thank_you')

        # Deleting field 'Party.guests_can_invite'
        db.delete_column('main_party', 'guests_can_invite')


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
        'main.cart': {
            'Meta': {'object_name': 'Cart'},
            'adds': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.LineItem']", 'symmetrical': 'False'}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Party']", 'null': 'True'}),
            'receiver': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'receiver'", 'null': 'True', 'to': "orm['auth.User']"}),
            'removes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'views': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'main.contactreason': {
            'Meta': {'object_name': 'ContactReason'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'main.contactrequest': {
            'Meta': {'object_name': 'ContactRequest'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.ContactReason']"}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        'main.customizeorder': {
            'Meta': {'object_name': 'CustomizeOrder'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sparkling': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'wine_mix': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'main.engagementinterest': {
            'Meta': {'object_name': 'EngagementInterest'},
            'engagement_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'main.invitationsent': {
            'Meta': {'object_name': 'InvitationSent'},
            'custom_message': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'custom_subject': ('django.db.models.fields.CharField', [], {'default': '"You\'re invited to a Vinely Party!"', 'max_length': '128'}),
            'guests': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Party']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'main.lineitem': {
            'Meta': {'object_name': 'LineItem'},
            'frequency': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price_category': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Product']", 'null': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'total_price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '10', 'decimal_places': '2'})
        },
        'main.myhost': {
            'Meta': {'object_name': 'MyHost'},
            'email_entered': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'my_pro'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pro': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'my_host'", 'null': 'True', 'to': "orm['auth.User']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'main.order': {
            'Meta': {'object_name': 'Order'},
            'carrier': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'cart': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Cart']", 'unique': 'True'}),
            'credit_card': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.CreditCard']", 'null': 'True'}),
            'fulfill_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'order_id': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'ordered_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ordered'", 'to': "orm['auth.User']"}),
            'receiver': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'received'", 'to': "orm['auth.User']"}),
            'ship_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'shipping_address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Address']", 'null': 'True'}),
            'stripe_card': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stripecard.StripeCard']", 'null': 'True'}),
            'tracking_number': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'main.orderreview': {
            'Meta': {'object_name': 'OrderReview'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Order']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'wine_rating': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personality.WineRatingData']"})
        },
        'main.organizedparty': {
            'Meta': {'object_name': 'OrganizedParty'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Party']"}),
            'pro': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'main.party': {
            'Meta': {'object_name': 'Party'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Address']"}),
            'auto_invite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'auto_thank_you': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'event_date': ('django.db.models.fields.DateTimeField', [], {}),
            'guests_can_invite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'main.partyinvite': {
            'Meta': {'object_name': 'PartyInvite'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'my_guests'", 'null': 'True', 'to': "orm['auth.User']"}),
            'invited_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'invitee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'my_invites'", 'to': "orm['auth.User']"}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Party']"}),
            'response': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'response_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'rsvp_code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'main.personalog': {
            'Meta': {'object_name': 'PersonaLog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Party']", 'null': 'True'}),
            'pro': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'personality_acquired'", 'null': 'True', 'to': "orm['auth.User']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'personality_found'", 'unique': 'True', 'to': "orm['auth.User']"})
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
        },
        'main.prosignuplog': {
            'Meta': {'object_name': 'ProSignupLog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mentor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'new_mentees'", 'null': 'True', 'to': "orm['auth.User']"}),
            'mentor_email': ('django.db.models.fields.CharField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'new_pro': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'main.thankyounote': {
            'Meta': {'object_name': 'ThankYouNote'},
            'custom_message': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'custom_subject': ('django.db.models.fields.CharField', [], {'default': "'Thanks for Attending My Vinely Taste Party!'", 'max_length': '128'}),
            'guests': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Party']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'personality.wine': {
            'Meta': {'object_name': 'Wine'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'added': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deactivated': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '10', 'decimal_places': '2'}),
            'sip_bits': ('django.db.models.fields.TextField', [], {}),
            'year': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'personality.wineratingdata': {
            'Meta': {'object_name': 'WineRatingData'},
            'dnl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overall': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sizzle': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sizzle_dnl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sweet': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sweet_dnl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'texture': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'texture_dnl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'weight_dnl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'wine': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personality.Wine']"})
        },
        'stripecard.stripecard': {
            'Meta': {'object_name': 'StripeCard'},
            'billing_zipcode': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'card_type': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '16'}),
            'exp_month': ('django.db.models.fields.IntegerField', [], {}),
            'exp_year': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_four': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'stripe_user': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['main']