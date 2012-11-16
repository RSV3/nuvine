# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."
        host_header = 'Where’s the wine party? Your place!'
        host_sub_header = '<span></span>'
        host_content = '''
        <h1>WHERE'S THE WINE PARTY? YOUR PLACE!</h1>
        <p>Host a lighthearted, private wine tasting with friends, discover your very own wine personality, and earn rewards from Vinely. How?</p>

        <h2>Find Some Time.</h2>
        <p>Schedule a Vinely Taste Party and you’ll be on your way to a very tasteful experience. You can either organize the party with a Pro you know, or we can find one for you.</p>

        <h2>Find Some Friends.</h2>
        <p>You got ‘em, so get ‘em to your place! We recommend 8 – 12 people. Your Vinely Pro will be glad to help you through the party planning process. </p>

        <h2>Order a Tasting Kit.</h2>
        <p>Order a Tasting Kit from Vinely.com. It’s quick and easy. Kits start at $75 and include six wines and everything you need for (?) guests to sip, savor, and rate. </p>

        <h2>Get rewarded.</h2>
        <p>At the Taste Party, guests can place orders based on their personality. The more they order, the more rewards you get! </p>
        '''

        pro_header = 'Where’s the wine party? Your place!'
        pro_sub_header = '<span></span>'
        pro_content = '''
        <h1>Want to conduct vinely taste parties and get paid to do it?</h1>

        <p>Help people discover their true taste in wine, and earn money while doing it! Vinely makes it easy for you to lead tasters through the learning experience. It’s simple, fun, and best of all, it’s profitable!</p>

        <h2>Find a Group</h2>
        <p>Identify hosts who want to invite friends or family to their homes for a Vinely Taste Party. Also, if we get contacted by a host who doesn’t know a Pro, we may introduce you.</p>

        <h2>Guide the Party</h2>
        <p>Conducting a party is simple and fun. As a Pro, you’ll help the host set up before the party and ensure the tasting goes according to the party plan. No wine experience needed! We’ll provide the training and tools to make sure you succeed.</p>

        <h2>Uncover Personalities</h2>
        <p>Once tasters have sipped and savored, you’ll be able to input their ratings into the Vinely web-based system, which quickly identifies each guest’s individual Wine Personality.</p>

        <h2>Help Place Orders</h2>
        <p>Lead guests through the ordering process on Vinely.com. All transactions are then processed by Vinely.</p>

        </h2>Get Paid</h2>
        <p>You’ll earn based on the success of each party! </p>
        '''

        host_template = orm['cms.ContentTemplate'].objects.create(key="make_host", category=1)
        orm['cms.Section'].objects.create(content=host_content, template=host_template, category=0)
        orm['cms.Section'].objects.create(content=host_header, template=host_template, category=4)
        orm['cms.Section'].objects.create(content=host_sub_header, template=host_template, category=5)

        pro_template = orm['cms.ContentTemplate'].objects.create(key="make_pro", category=1)
        orm['cms.Section'].objects.create(content=pro_content, template=pro_template, category=0)
        orm['cms.Section'].objects.create(content=pro_header, template=pro_template, category=4)
        orm['cms.Section'].objects.create(content=pro_sub_header, template=pro_template, category=5)

    def backwards(self, orm):
        "Write your backwards methods here."
        templates = orm['cms.ContentTemplate'].objects.filter(key__in=['make_host', 'make_pro'])
        sections = orm['cms.Section'].objects.filter(template__in=templates)
        sections.delete()
        templates.delete()

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
            'category': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
