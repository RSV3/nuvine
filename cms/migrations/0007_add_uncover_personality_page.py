# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."
        template = orm.ContentTemplate.objects.create(key='uncover_personality', category=1)
        
        content = """
        <p>Your Vinely Wine Personality is determined by the flavor preferences that characterize your taste in wine. </p>

        <p>You can uncover yours at a Vinely Taste Party, where you’ll sip, savor, and rate wines with your friends. 
        Vinely takes your feedback and runs it through a system developed by leading wine experts and scientists. 
        The system uses this information to uncover your unique taste characteristics and reveals your wine personality. </p>

        <p>Will you be Whimsical, Serendipitous, Sensational, Exuberant, Moxie, or Easygoing?</p>

        <p>Curious to find out? Learn how!</p>

        """
        orm.Section.objects.create(category=0, content=content, template=template)
        content = "So, you want to uncover your wine personality?"
        orm.Section.objects.create(category=4, content=content, template=template)

    def backwards(self, orm):
        "Write your backwards methods here."
        template = orm.ContentTemplate.objects.get(key='uncover_personality')

        orm.Section.objects.filter(category=0, template=template).delete()
        content = "So, you want to uncover your wine personality?"
        orm.Section.objects.filter(category=4, template=template).delete()
        template.delete()

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
