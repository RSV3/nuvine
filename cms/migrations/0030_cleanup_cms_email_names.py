# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."
        orm.ContentTemplate.objects.filter(key='welcome_email').update(name='Account verification')
        orm.ContentTemplate.objects.filter(key='unknown_pro_party_email').update(name='New host confirmation, awaiting Pro')
        orm.ContentTemplate.objects.filter(key='rsvp_thank_you_email').update(name='Event RSVP confirmation')
        orm.ContentTemplate.objects.filter(key='pro_review_email').update(name='New pro request to care')
        orm.ContentTemplate.objects.filter(key='pro_request_email').update(name='Pro request confirmation to pro')
        orm.ContentTemplate.objects.filter(key='pro_approved_email').update(name='Pro approved confirmaiton ')
        orm.ContentTemplate.objects.filter(key='password_change_email').update(name='Forgot password email')
        orm.ContentTemplate.objects.filter(key='party_setup_completed_email').update(name='Party setup completed to pro')
        orm.ContentTemplate.objects.filter(key='order_confirmation_email').update(name='Order confirmation email')
        orm.ContentTemplate.objects.filter(key='not_in_area_party_email').update(name='Not in your area notification')
        orm.ContentTemplate.objects.filter(key='new_party_host_confirm_email').update(name='Notification to finish party setup')
        orm.ContentTemplate.objects.filter(key='mentor_assigned_notification_email').update(name='Mentor assigned notification')
        orm.ContentTemplate.objects.filter(key='mentee_assigned_notification_email').update(name='Mentee assigned notification')
        orm.ContentTemplate.objects.filter(key='know_pro_party_email').update(name='Party requested, known pro')
        orm.ContentTemplate.objects.filter(key='join_the_club_anon_email').update(name='Join the club confirmation (anon. user)')
        orm.ContentTemplate.objects.filter(key='host_vinely_party_email').update(name='Notification of new party to pro')
        orm.ContentTemplate.objects.filter(key='contact_request_email').update(name='Company contact request')
        orm.ContentTemplate.objects.filter(key='contact_request_email').update(name='Company contact request')
        orm.ContentTemplate.objects.filter(key='contact_request_email').update(name='Company contact request')
        orm.ContentTemplate.objects.filter(key='distribute_party_thanks_note_email').update(name='distribute_party_thanks_note_email')
        orm.ContentTemplate.objects.filter(key='distribute_party_invites_email').update(name='distribute_party_invites_email')
        orm.ContentTemplate.objects.filter(key='order_shipped_email').update(name='order_shipped_email')

        # deactivate unused emails
        orm.ContentTemplate.objects.filter(key='verification_email').update(active=False)
        orm.ContentTemplate.objects.filter(key='signed_up_as_host_email').update(active=False)
        orm.ContentTemplate.objects.filter(key='pro_assigned_notification_email').update(active=False)
        orm.ContentTemplate.objects.filter(key='new_party_scheduled_email').update(active=False)
        orm.ContentTemplate.objects.filter(key='new_party_scheduled_by_host_no_pro_email').update(active=False)
        orm.ContentTemplate.objects.filter(key='new_party_scheduled_by_host_email').update(active=False)
        orm.ContentTemplate.objects.filter(key='new_party_email').update(active=False)
        orm.ContentTemplate.objects.filter(key='new_invitation_email').update(active=False)
        orm.ContentTemplate.objects.filter(key='host_request_party_email').update(active=False)
        orm.ContentTemplate.objects.filter(key='account_activiation_email').update(active=False)

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        'cms.contenttemplate': {
            'Meta': {'ordering': "['category', '-key']", 'object_name': 'ContentTemplate'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'variables_legend': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cms.Variable']", 'symmetrical': 'False'})
        },
        'cms.section': {
            'Meta': {'object_name': 'Section'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sections'", 'to': "orm['cms.ContentTemplate']"})
        },
        'cms.variable': {
            'Meta': {'object_name': 'Variable'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'var': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['cms']
    symmetrical = True
