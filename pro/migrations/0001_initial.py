# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProLevel'
        db.create_table('pro_prolevel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('level', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('pro', ['ProLevel'])

        # Adding model 'ProLevelLog'
        db.create_table('pro_prolevellog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('level', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('pro', ['ProLevelLog'])

        # Adding model 'WeeklyCompensation'
        db.create_table('pro_weeklycompensation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pro', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('total_personal_sales', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('tier_a_personal_sales', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('tier_b_personal_sales', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('total_earnings', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('tier_a_base_earnings', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('tier_b_base_earnings', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('pro', ['WeeklyCompensation'])

        # Adding model 'MonthlyQualification'
        db.create_table('pro_monthlyqualification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pro', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('total_personal_sales', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('total_sales_1st_line', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('active_pros', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('advanced_pros', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('elite_pros', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('qualification_level', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('pro', ['MonthlyQualification'])

        # Adding model 'MonthlyBonusCompensation'
        db.create_table('pro_monthlybonuscompensation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pro', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('qualification_level', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('total_personal_sales', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('tier_a_personal_sales', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('tier_b_personal_sales', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('total_first_downline_sales', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('total_second_downline_sales', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('total_third_downline_sales', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('tier_a_bonus', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('tier_b_bonus', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('first_line_bonus', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('second_line_bonus', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('third_line_bonus', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('pro', ['MonthlyBonusCompensation'])


    def backwards(self, orm):
        # Deleting model 'ProLevel'
        db.delete_table('pro_prolevel')

        # Deleting model 'ProLevelLog'
        db.delete_table('pro_prolevellog')

        # Deleting model 'WeeklyCompensation'
        db.delete_table('pro_weeklycompensation')

        # Deleting model 'MonthlyQualification'
        db.delete_table('pro_monthlyqualification')

        # Deleting model 'MonthlyBonusCompensation'
        db.delete_table('pro_monthlybonuscompensation')


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
        'pro.monthlybonuscompensation': {
            'Meta': {'object_name': 'MonthlyBonusCompensation'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'first_line_bonus': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pro': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'qualification_level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'second_line_bonus': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'third_line_bonus': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'tier_a_bonus': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'tier_a_personal_sales': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'tier_b_bonus': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'tier_b_personal_sales': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'total_first_downline_sales': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'total_personal_sales': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'total_second_downline_sales': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'total_third_downline_sales': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'})
        },
        'pro.monthlyqualification': {
            'Meta': {'object_name': 'MonthlyQualification'},
            'active_pros': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'advanced_pros': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'elite_pros': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pro': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'qualification_level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'total_personal_sales': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'total_sales_1st_line': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'})
        },
        'pro.prolevel': {
            'Meta': {'object_name': 'ProLevel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'pro.prolevellog': {
            'Meta': {'object_name': 'ProLevelLog'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'pro.weeklycompensation': {
            'Meta': {'object_name': 'WeeklyCompensation'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pro': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'tier_a_base_earnings': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'tier_a_personal_sales': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'tier_b_base_earnings': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'tier_b_personal_sales': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'total_earnings': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'total_personal_sales': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'})
        }
    }

    complete_apps = ['pro']