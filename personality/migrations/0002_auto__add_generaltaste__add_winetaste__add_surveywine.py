# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GeneralTaste'
        db.create_table('personality_generaltaste', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('drink_regularly', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('coffee_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('coffee_take', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('salty_food', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('citrus', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('earthy', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('berries', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('artificial', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('new_flavors', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('personality', ['GeneralTaste'])

        # Adding model 'WineTaste'
        db.create_table('personality_winetaste', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('typically_drink', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('red_body', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('red_sweetness', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('red_acidity', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('red_color', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('red_wines_other', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('red_wine_dislike', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='survey_red_dislike', null=True, to=orm['personality.SurveyWine'])),
            ('red_wine_dislike_other', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('white_oak', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('white_sweetness', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('white_acidity', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('white_color', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('white_wines_other', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('white_wine_dislike', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='survey_white_dislike', null=True, to=orm['personality.SurveyWine'])),
            ('white_wine_dislike_other', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
        ))
        db.send_create_signal('personality', ['WineTaste'])

        # Adding M2M table for field red_wines_often on 'WineTaste'
        db.create_table('personality_winetaste_red_wines_often', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('winetaste', models.ForeignKey(orm['personality.winetaste'], null=False)),
            ('surveywine', models.ForeignKey(orm['personality.surveywine'], null=False))
        ))
        db.create_unique('personality_winetaste_red_wines_often', ['winetaste_id', 'surveywine_id'])

        # Adding M2M table for field white_wines_often on 'WineTaste'
        db.create_table('personality_winetaste_white_wines_often', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('winetaste', models.ForeignKey(orm['personality.winetaste'], null=False)),
            ('surveywine', models.ForeignKey(orm['personality.surveywine'], null=False))
        ))
        db.create_unique('personality_winetaste_white_wines_often', ['winetaste_id', 'surveywine_id'])

        # Adding M2M table for field other_wines on 'WineTaste'
        db.create_table('personality_winetaste_other_wines', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('winetaste', models.ForeignKey(orm['personality.winetaste'], null=False)),
            ('surveywine', models.ForeignKey(orm['personality.surveywine'], null=False))
        ))
        db.create_unique('personality_winetaste_other_wines', ['winetaste_id', 'surveywine_id'])

        # Adding model 'SurveyWine'
        db.create_table('personality_surveywine', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('color', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('personality', ['SurveyWine'])


    def backwards(self, orm):
        # Deleting model 'GeneralTaste'
        db.delete_table('personality_generaltaste')

        # Deleting model 'WineTaste'
        db.delete_table('personality_winetaste')

        # Removing M2M table for field red_wines_often on 'WineTaste'
        db.delete_table('personality_winetaste_red_wines_often')

        # Removing M2M table for field white_wines_often on 'WineTaste'
        db.delete_table('personality_winetaste_white_wines_often')

        # Removing M2M table for field other_wines on 'WineTaste'
        db.delete_table('personality_winetaste_other_wines')

        # Deleting model 'SurveyWine'
        db.delete_table('personality_surveywine')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'personality.generaltaste': {
            'Meta': {'object_name': 'GeneralTaste'},
            'artificial': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'berries': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'citrus': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'coffee_take': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'coffee_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'drink_regularly': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'earthy': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_flavors': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'salty_food': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'personality.surveywine': {
            'Meta': {'object_name': 'SurveyWine'},
            'color': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'personality.wine': {
            'Meta': {'object_name': 'Wine'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'added': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deactivated': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '10', 'decimal_places': '2'}),
            'sip_bits': ('django.db.models.fields.TextField', [], {}),
            'year': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'personality.winepersonality': {
            'Meta': {'object_name': 'WinePersonality'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'personality.wineratingdata': {
            'Meta': {'object_name': 'WineRatingData'},
            'dnl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overall': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sizzle': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sizzle_dnl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sweet': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sweet_dnl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'texture': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'texture_dnl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'weight_dnl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'wine': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personality.Wine']"})
        },
        'personality.winetaste': {
            'Meta': {'object_name': 'WineTaste'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'other_wines': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'other_likes'", 'symmetrical': 'False', 'to': "orm['personality.SurveyWine']"}),
            'red_acidity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'red_body': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'red_color': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'red_sweetness': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'red_wine_dislike': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'survey_red_dislike'", 'null': 'True', 'to': "orm['personality.SurveyWine']"}),
            'red_wine_dislike_other': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'red_wines_often': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'survey_red_favorites'", 'symmetrical': 'False', 'to': "orm['personality.SurveyWine']"}),
            'red_wines_other': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'typically_drink': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'white_acidity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'white_color': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'white_oak': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'white_sweetness': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'white_wine_dislike': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'survey_white_dislike'", 'null': 'True', 'to': "orm['personality.SurveyWine']"}),
            'white_wine_dislike_other': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'white_wines_often': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'survey_white_favorites'", 'symmetrical': 'False', 'to': "orm['personality.SurveyWine']"}),
            'white_wines_other': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['personality']