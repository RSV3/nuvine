# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."
        content = """

        Welcome to the club! We are delighted you've decided to let Vinely make your wine experience easy, fun, and convenient.
        You're in good hands.

        Your first delicious surprise will arrive within 7 - 10 business days.
        Remember, someone 21 years or older must be available to receive your shipment.

        This first shipment is your Vinely First Taste Experience. It will include 6 wines and an experience booklet.
        As you taste these wines, make sure to record your ratings, and input them to the website by logging into Vinely.com,
        and clicking 'Rate Wines'.

        This will allow us to assign you a wine personality and begin the process of delivering a perfectly personalized selection of wine right to your door each month.
        Happy Tasting!

        {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

        Your Tasteful Friends,

        - The Vinely Team

        """

        template, created = orm.ContentTemplate.objects.get_or_create(key="join_the_club_anon_email", category=0)
        section, created = orm.Section.objects.get_or_create(category=0, template=template)
        section.content = content
        section.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        template = orm.ContentTemplate.objects.get(key="join_the_club_anon_email")
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
