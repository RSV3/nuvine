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
        {{ invite_host_name }},

        I'm so excited to lead your Vinely Party on <b>{{ party.event_date|date:"F j, o" }}</b> at <b>{{ party.event_date|date:"g:i A" }}</b>!
        Your party has been scheduled in the system using the information you provided (see below).
        You are now all set to invite your friends and order your tasting kit!

        Party: "{{ party.title }}"

        Date: {{ party.event_date|date:"F j, o" }}

        Time: {{ party.event_date|date:"g:i A" }}

        Location: {{ party.address.full_text }}

        If any changes need to be made, you run into any trouble, or have any questions please contact me at {{ pro.email }}{% if pro_phone %} or {{ pro_phone }}{% endif %}.

        <strong>When you are ready, <a href="http://{{ host_name }}{% url party_add party.id %}">click here</a> to get started.</strong>

        Tastefully,

        - {{ pro_name }}

        """
        template, created = orm.ContentTemplate.objects.get_or_create(key="new_party_host_confirm_email", category=0)
        section, created = orm.Section.objects.get_or_create(category=0, template=template)
        section.content = content
        section.save()

        variable, created = orm.Variable.objects.get_or_create(var="{{ invite_host_name }}", description="Name of the party host")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ party.title }}", description="Name of the party")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ party.event_date }}", description="Date of the event")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ pro.email }}", description="Vinely Pro's email address")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ pro_phone }}", description="Vinely Pro's phone number")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ pro_name }}", description="Name of the Vinely Pro")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="http://{{ host_name }}{% url party_add party.id %}",
                                                description="Link to party editing page")
        template.variables_legend.add(variable)

    def backwards(self, orm):
        "Write your backwards methods here."
        template = orm.ContentTemplate.objects.get(key="new_party_host_confirm_email", category=0)
        orm.Section.objects.filter(category=0, template=template).delete()
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
