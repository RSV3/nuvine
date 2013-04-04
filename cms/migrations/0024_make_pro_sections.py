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
        MAKE WORK SOCIAL, FLEXIBLE & FUN!
        """
        content_overview = """
        <p>Becoming a Vinely Pro is a fun, flexible opportunity where you can earn extra income or even replace your day job.</p>

        <p>It doesn’t feel like work when you get to make new friends, build your own team,
        and help people find wine they love all while at a party.</p>
        """

        content_parties = """
        <p>The job starts with parties. Not bad, right? A Pro guides tasters through a fun wine-tasting experience and collects orders.
        Vinely handles the rest, including payments and wine deliveries.
        You probably know lots of people who like to entertain, drink wine, or simply have fun...these are your party hosts.
        Start thinking your first few hosts now!</p>
        """

        content_earnings = """
        <p>With three ways to earn, your Vinely income can really begin to stack up!
        First, earn on all retail sales of wine.
        Second, earn residual income on all subscription shipments of wine club members.
        And third, build a team to earn on sales of Pro’s who you bring into the Vinely business.</p>
        """

        content_support = """
        <p>When you join the team, you’ll get access to live training, marketing materials, webinars, videos, and plenty of individual TLC.
        Our goal is to help you grow your very own wine business into a huge success!</p>
        """

        content_growth = """
        <p>
        As a Pro, your success is based on effort and performance.
        As you grow your business, you have the opportunity to earn significant income,
        and lead others towards accomplishing their goals by building and nurturing a successful team!
        </p>
        """

        template, created = orm.ContentTemplate.objects.get_or_create(key="make_pro", category=1)
        section, created = orm.Section.objects.get_or_create(key="header", template=template)
        section.content = content_header
        section.save()
        section, created = orm.Section.objects.get_or_create(key="overview", template=template)
        section.content = content_overview
        section.save()
        section, created = orm.Section.objects.get_or_create(key="parties", template=template)
        section.content = content_parties
        section.save()
        section, created = orm.Section.objects.get_or_create(key="earnings", template=template)
        section.content = content_earnings
        section.save()
        section, created = orm.Section.objects.get_or_create(key="support", template=template)
        section.content = content_support
        section.save()
        section, created = orm.Section.objects.get_or_create(key="growth", template=template)
        section.content = content_growth
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
