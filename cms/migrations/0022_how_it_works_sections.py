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
        <p>The Vinely Experience uses your taste buds and a little technology to find your "Wine Personality"</p>

        <p>Just taste, rate and order to receive your perfectly matched wines right to your doorstep.</p>

        <p>You never have to worry again because we 100% <u>guarantee</u> your taste buds will love the wines we deliver.</p>
        """

        content_taste = """
        <p>Get started with your tasting experience. Enjoy your way through 6 bottles to set the wheels in motion.</p>

        <p>Feeling social? Host a Host a Vinely Party! Invite 8-12 friends to join you for a tasting party.</p>

        <p>Feeling independent? Sip solo and your tastes in your own space and your own time.</p>
        """

        content_rate = """
        Rate the six carefully selected tasting wines in your Experience Booklet.
        Each rating provides an insight we'll use to uncover your tastes in wine and reveal your "Wine personality".
        You might be Whimsical, Exuberation, Sensational, Moxie, Easygoing or Serendipitous.

        """
        content_order = """
        <p>Place an order to receive wines that you're sure to love.
        We will select a range of unique wines to match your tastes, and deliver them right to your door.</p>

        <p>Vinely VIPs can enjoy monthly shipments (upto 144 wines per year),
        with a continually improving selection based on your feedback ratings.
        Shipping is free and you may cancel anytime.</p>

        <p>Here's the best part...your satisfaction is 100% money-back guaranteed...
        (Have you ever tried to return an opened bottle of wine to the store? Enough said).</p>
        """
        content_repeat = """
        <p>Did you like it? Love it? The more you drink the better we get to know you.
        Giving Vinely feedback helps us continually improve your personalized wine selection with each shipment</p>
        """

        template, created = orm.ContentTemplate.objects.get_or_create(key="how_it_works", category=1)
        section, created = orm.Section.objects.get_or_create(key="overview", template=template)
        section.content = content_overview
        section.save()
        section, created = orm.Section.objects.get_or_create(key="taste", template=template)
        section.content = content_taste
        section.save()
        section, created = orm.Section.objects.get_or_create(key="rate", template=template)
        section.content = content_rate
        section.save()
        section, created = orm.Section.objects.get_or_create(key="order", template=template)
        section.content = content_order
        section.save()
        section, created = orm.Section.objects.get_or_create(key="repeat", template=template)
        section.content = content_repeat
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
