# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."
        content_overview = """
        <p>You're social and you love wine. Why not benefit by having the Vinely Experience in your home?</p>

        <p>Signup to host a party and one of our carefully trained experts, or as we call them, our Vinely Pros,
        will handle the heavy lifting. Isn't it great when you can enjoy your own party?</p>

        <p>Your friends will think you're the host with the most when you introduce them to their Wine Personality.</p>
        """

        content_people = """
        <p>Think friends, relatives, neighbors, co-workers...anyone over 21 who likes wine and a good time.</p>
        """

        content_place = """
        <p>Staying in is the new going out with Vinely.</p>
        <p>Enjoy your Vinely experience anywhere so long as you can fit 12 people.
        Any night can be turned into time with friends, a corporate retreat or a neighbourhood gathering.</p>
        """

        content_rewards = """
        <p>Lots and lots of rewards!!!</p>
        """

        content_order = """
        <p>
        Order your tasting experience ($99) which includes 6 bottles of wine and other tasting supplies.
        This should be ordered 2 weeks prior to the party to ensure plenty of time to choose music and food for your party
        (artisan, crackers, stuffed mushrooms, best of the 80's?)
        </p>
        """

        template, created = orm.ContentTemplate.objects.get_or_create(key="make_host", category=1)
        section, created = orm.Section.objects.get_or_create(key="overview", template=template)
        section.content = content_overview
        section.save()
        section, created = orm.Section.objects.get_or_create(key="people", template=template)
        section.content = content_people
        section.save()
        section, created = orm.Section.objects.get_or_create(key="place", template=template)
        section.content = content_place
        section.save()
        section, created = orm.Section.objects.get_or_create(key="rewards", template=template)
        section.content = content_rewards
        section.save()
        section, created = orm.Section.objects.get_or_create(key="order", template=template)
        section.content = content_order
        section.save()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        'cms.contenttemplate': {
            'Meta': {'ordering': "['category', '-key']", 'object_name': 'ContentTemplate'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'variables_legend': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cms.Variable']", 'symmetrical': 'False'})
        },
        'cms.section': {
            'Meta': {'object_name': 'Section'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
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
