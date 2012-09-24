# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Section'
        db.create_table('cms_section', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cms.ContentTemplate'])),
        ))
        db.send_create_signal('cms', ['Section'])

        # Deleting field 'ContentTemplate.content'
        db.delete_column('cms_contenttemplate', 'content')


    def backwards(self, orm):
        # Deleting model 'Section'
        db.delete_table('cms_section')

        # Adding field 'ContentTemplate.content'
        db.add_column('cms_contenttemplate', 'content',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)


    models = {
        'cms.contenttemplate': {
            'Meta': {'object_name': 'ContentTemplate'},
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
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.ContentTemplate']"})
        },
        'cms.variable': {
            'Meta': {'object_name': 'Variable'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'var': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['cms']