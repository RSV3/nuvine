# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Variable'
        db.create_table('cms_variable', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('var', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('cms', ['Variable'])

        # Adding model 'ContentTemplate'
        db.create_table('cms_contenttemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('category', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('cms', ['ContentTemplate'])

        # Adding M2M table for field variables_legend on 'ContentTemplate'
        db.create_table('cms_contenttemplate_variables_legend', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contenttemplate', models.ForeignKey(orm['cms.contenttemplate'], null=False)),
            ('variable', models.ForeignKey(orm['cms.variable'], null=False))
        ))
        db.create_unique('cms_contenttemplate_variables_legend', ['contenttemplate_id', 'variable_id'])


    def backwards(self, orm):
        # Deleting model 'Variable'
        db.delete_table('cms_variable')

        # Deleting model 'ContentTemplate'
        db.delete_table('cms_contenttemplate')

        # Removing M2M table for field variables_legend on 'ContentTemplate'
        db.delete_table('cms_contenttemplate_variables_legend')


    models = {
        'cms.contenttemplate': {
            'Meta': {'object_name': 'ContentTemplate'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'variables_legend': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cms.Variable']", 'symmetrical': 'False'})
        },
        'cms.variable': {
            'Meta': {'object_name': 'Variable'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'var': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['cms']