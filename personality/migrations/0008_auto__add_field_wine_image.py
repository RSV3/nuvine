# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Wine.image'
        db.add_column('personality_wine', 'image',
                      self.gf('sorl.thumbnail.fields.ImageField')(max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Wine.image'
        db.delete_column('personality_wine', 'image')


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
            'coffee_take': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'coffee_type': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'drink_regularly': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'earthy': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_flavors': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'salty_food': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'personality.surveywine': {
            'Meta': {'object_name': 'SurveyWine'},
            'color': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'personality.tastingkit': {
            'Meta': {'object_name': 'TastingKit'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '10', 'decimal_places': '2'}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'personality.wine': {
            'Meta': {'object_name': 'Wine'},
            'acidity': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'alcohol': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'body': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'color': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'deactivated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'enclosure': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fruit': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'is_taste_kit_wine': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'oak': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'ph': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '10', 'decimal_places': '2'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'residual_sugar': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'sip_bits': ('django.db.models.fields.TextField', [], {}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'sparkling': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'supplier': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'tannin': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'varietal': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'vinely_category': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'vinely_category2': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'year': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'personality.winepersonality': {
            'Meta': {'object_name': 'WinePersonality'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'personality.wineratingdata': {
            'Meta': {'ordering': "['wine__number']", 'object_name': 'WineRatingData'},
            'dnl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overall': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sizzle': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sizzle_dnl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sweet': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sweet_dnl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'texture': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'texture_dnl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'weight_dnl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'wine': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personality.Wine']"})
        },
        'personality.winetaste': {
            'Meta': {'object_name': 'WineTaste'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'other_wines': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'other_likes'", 'symmetrical': 'False', 'to': "orm['personality.SurveyWine']"}),
            'red_acidity': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'red_body': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'red_color': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'red_sweetness': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'red_wine_dislike': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'survey_red_dislike'", 'null': 'True', 'to': "orm['personality.SurveyWine']"}),
            'red_wine_dislike_other': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'red_wines_often': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'survey_red_favorites'", 'symmetrical': 'False', 'to': "orm['personality.SurveyWine']"}),
            'red_wines_other': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'typically_drink': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'white_acidity': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'white_color': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'white_oak': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'white_sweetness': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'white_wine_dislike': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'survey_white_dislike'", 'null': 'True', 'to': "orm['personality.SurveyWine']"}),
            'white_wine_dislike_other': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'white_wines_often': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'survey_white_favorites'", 'symmetrical': 'False', 'to': "orm['personality.SurveyWine']"}),
            'white_wines_other': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['personality']