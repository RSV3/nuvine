# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."

        content_header = """
        Change the way you experience wine
        """

        content_overview1 = """
        Tired of the guesswork of buying wine? Now Vinely makes it easy, convenient and fun.
        """

        content_overview2 = """
        The Vinely experience is as simple as Sip, Rate and Repeat.
        Treat your taste buds to wines you're guaranteed to love delivered right to your door.
        """

        content_host_section = """
        <h1>Host a party</h1>
        <p>
        Pop the cork! <br/>
        Learn about hosting <br />
        a Vinely party
        </p>
        """

        content_pro_section = """
        <h1>Join the team</h1>
        <p>
        Take it to the next level <br/>
        to earn a little or <br />
        a lot...it's up to you!
        </p>
        """

        template, created = orm.ContentTemplate.objects.get_or_create(key="landing_page", category=1)
        section, created = orm.Section.objects.get_or_create(key="header", template=template)
        section.content = content_header
        section.save()
        section, created = orm.Section.objects.get_or_create(key="overview_col1", template=template)
        section.content = content_overview1
        section.save()
        section, created = orm.Section.objects.get_or_create(key="overview_col2", template=template)
        section.content = content_overview2
        section.save()
        section, created = orm.Section.objects.get_or_create(key="host", template=template)
        section.content = content_host_section
        section.save()
        section, created = orm.Section.objects.get_or_create(key="pro", template=template)
        section.content = content_pro_section
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
