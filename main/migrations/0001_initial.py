# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ContactReason'
        db.create_table('main_contactreason', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal('main', ['ContactReason'])

        # Adding model 'ContactRequest'
        db.create_table('main_contactrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.ContactReason'])),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('sex', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=12)),
        ))
        db.send_create_signal('main', ['ContactRequest'])

        # Adding model 'Party'
        db.create_table('main_party', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Address'])),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('event_date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('main', ['Party'])

        # Adding model 'PartyInvite'
        db.create_table('main_partyinvite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('party', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Party'])),
            ('invitee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='my_invites', to=orm['auth.User'])),
            ('invited_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='my_guests', null=True, to=orm['auth.User'])),
            ('response', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('invited_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('response_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('main', ['PartyInvite'])

        # Adding model 'PersonaLog'
        db.create_table('main_personalog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='personality_found', unique=True, to=orm['auth.User'])),
            ('party', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Party'], null=True)),
            ('pro', self.gf('django.db.models.fields.related.ForeignKey')(related_name='personality_acquired', null=True, to=orm['auth.User'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['PersonaLog'])

        # Adding model 'Product'
        db.create_table('main_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('sku', self.gf('django.db.models.fields.CharField')(default='xxxxxxxxxxxxxxxxxxxxxxxxxx', max_length=32)),
            ('category', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('unit_price', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=10, decimal_places=2)),
            ('image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100)),
            ('cart_tag', self.gf('django.db.models.fields.CharField')(default='x', max_length=64)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['Product'])

        # Adding model 'LineItem'
        db.create_table('main_lineitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Product'], null=True)),
            ('price_category', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('frequency', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('total_price', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=10, decimal_places=2)),
        ))
        db.send_create_signal('main', ['LineItem'])

        # Adding model 'Cart'
        db.create_table('main_cart', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('party', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Party'], null=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('adds', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('removes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('views', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('main', ['Cart'])

        # Adding M2M table for field items on 'Cart'
        db.create_table('main_cart_items', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cart', models.ForeignKey(orm['main.cart'], null=False)),
            ('lineitem', models.ForeignKey(orm['main.lineitem'], null=False))
        ))
        db.create_unique('main_cart_items', ['cart_id', 'lineitem_id'])

        # Adding model 'Order'
        db.create_table('main_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ordered_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ordered', to=orm['auth.User'])),
            ('receiver', self.gf('django.db.models.fields.related.ForeignKey')(related_name='received', to=orm['auth.User'])),
            ('order_id', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('cart', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['main.Cart'], unique=True)),
            ('shipping_address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Address'], null=True)),
            ('credit_card', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CreditCard'], null=True)),
            ('order_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('fulfill_status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('carrier', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('tracking_number', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('ship_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('main', ['Order'])

        # Adding model 'OrderReview'
        db.create_table('main_orderreview', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Order'])),
            ('wine_rating', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personality.WineRatingData'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['OrderReview'])

        # Adding model 'OrganizedParty'
        db.create_table('main_organizedparty', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pro', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('party', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Party'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['OrganizedParty'])

        # Adding model 'MyHost'
        db.create_table('main_myhost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pro', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='my_host', null=True, to=orm['auth.User'])),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(related_name='my_pro', to=orm['auth.User'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['MyHost'])

        # Adding model 'CustomizeOrder'
        db.create_table('main_customizeorder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('wine_mix', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('sparkling', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['CustomizeOrder'])

        # Adding model 'EngagementInterest'
        db.create_table('main_engagementinterest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('engagement_type', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('latest', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['EngagementInterest'])

        # Adding model 'InvitationSent'
        db.create_table('main_invitationsent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('party', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Party'])),
            ('custom_subject', self.gf('django.db.models.fields.CharField')(default="You're invited to a Vinely Party!", max_length=128)),
            ('custom_message', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('main', ['InvitationSent'])

        # Adding M2M table for field guests on 'InvitationSent'
        db.create_table('main_invitationsent_guests', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('invitationsent', models.ForeignKey(orm['main.invitationsent'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('main_invitationsent_guests', ['invitationsent_id', 'user_id'])


    def backwards(self, orm):
        # Deleting model 'ContactReason'
        db.delete_table('main_contactreason')

        # Deleting model 'ContactRequest'
        db.delete_table('main_contactrequest')

        # Deleting model 'Party'
        db.delete_table('main_party')

        # Deleting model 'PartyInvite'
        db.delete_table('main_partyinvite')

        # Deleting model 'PersonaLog'
        db.delete_table('main_personalog')

        # Deleting model 'Product'
        db.delete_table('main_product')

        # Deleting model 'LineItem'
        db.delete_table('main_lineitem')

        # Deleting model 'Cart'
        db.delete_table('main_cart')

        # Removing M2M table for field items on 'Cart'
        db.delete_table('main_cart_items')

        # Deleting model 'Order'
        db.delete_table('main_order')

        # Deleting model 'OrderReview'
        db.delete_table('main_orderreview')

        # Deleting model 'OrganizedParty'
        db.delete_table('main_organizedparty')

        # Deleting model 'MyHost'
        db.delete_table('main_myhost')

        # Deleting model 'CustomizeOrder'
        db.delete_table('main_customizeorder')

        # Deleting model 'EngagementInterest'
        db.delete_table('main_engagementinterest')

        # Deleting model 'InvitationSent'
        db.delete_table('main_invitationsent')

        # Removing M2M table for field guests on 'InvitationSent'
        db.delete_table('main_invitationsent_guests')


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
            'card_type': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '10'}),
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
            'engagement_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'main.invitationsent': {
            'Meta': {'object_name': 'InvitationSent'},
            'custom_message': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'custom_subject': ('django.db.models.fields.CharField', [], {'default': '"You\'re invited to a Vinely Party!"', 'max_length': '128'}),
            'guests': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
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
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'event_date': ('django.db.models.fields.DateTimeField', [], {}),
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
            'response_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'sku': ('django.db.models.fields.CharField', [], {'default': "'xxxxxxxxxxxxxxxxxxxxxxxxxx'", 'max_length': '32'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'unit_price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '10', 'decimal_places': '2'})
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
        }
    }

    complete_apps = ['main']