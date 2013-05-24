# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."

        host_header = 'Treat yourself to a club that\'s all about you'
        host_sub_header = '<span></span>'
        content_overview = """
        <p>Say hello to a future of wine that you are guaranteed to love.</p>

        <p>Join the exclusive Vinely club to learn your Wine Personality,
        gain access to member-only perks and receive delicious personalized,
        hand-picked wine delivered to your door every month</p>

        <p>Your friends will think you're the host with the most when you introduce them to their Wine Personality.</p>
        """

        content_anticipition = """
        <p>Are you Whimsical, Exuberant, Sensational, Moxie, Easygoing or Serendipitous? If you don't know, get drinking!</p>
        <p>Just sip and rate our 6 carefully selected First Taste Wines to uncover your Vinely Wine Personality.</p>
        """

        content_surprise = """
        <p>Who doesn't love a surprise, especially when you are guaranteed to love it?
        As a Vinely Club member you will eagerly await 6 different wines perfectly matched to your taste buds each month.
        Enhance your enjoyment every month with wine you love. One more surprise from us...we pay for shipping!</p>
        <p>This is a club where the deliveries are as unique as you!</p>
        """

        content_indulgence = """
        <p>You will be the envy of all your friends when every glass you pour is one you love.
        Give yourself the gift of easy wine enjoyment. Go ahead, you deserve it.</p>
        """

        content_excitement = """
        <p>
        Enjoy perks like member-only experiences, preview events, trips, gifts and items that express your personality.
        </p>
        """

        content_product = """
        <p>
          <ul id="membership">
            <li>6 unique bottles of wine each month</li>
            <li>Delivery right to your door, FREE</li>
            <li>Continually improving wines based on your ratings</li>
            <li>Satisfaction guaranteed. Period. Or your money back</li>
            <li>No risk. Cancel anytime, no questions asked!</li>
          </ul>
        </p>
        """
        template, created = orm.ContentTemplate.objects.get_or_create(key="join_club", category=1)
        section, created = orm.Section.objects.get_or_create(key='header', template=template)
        section.content = host_header
        section.save()
        section, created = orm.Section.objects.get_or_create(key='sub_header', template=template)
        section.content = host_sub_header
        section.save()
        section, created = orm.Section.objects.get_or_create(key="overview", template=template)
        section.content = content_overview
        section.save()
        section, created = orm.Section.objects.get_or_create(key="anticipation", template=template)
        section.content = content_anticipition
        section.save()
        section, created = orm.Section.objects.get_or_create(key="surprise", template=template)
        section.content = content_surprise
        section.save()
        section, created = orm.Section.objects.get_or_create(key="indulgence", template=template)
        section.content = content_indulgence
        section.save()
        section, created = orm.Section.objects.get_or_create(key="excitement", template=template)
        section.content = content_excitement
        section.save()
        section, created = orm.Section.objects.get_or_create(key="product", template=template)
        section.content = content_product
        section.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        template = orm.ContentTemplate.objects.get(key="join_club", category=1)
        orm.Section.objects.filter(template=template).delete()
        template.delete()

    models = {
        'cms.contenttemplate': {
            'Meta': {'ordering': "['category', '-key']", 'object_name': 'ContentTemplate'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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
