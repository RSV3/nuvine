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

        {% load static %}

        Thank you for attending "{{ party.title }}" on {{ party.event_date|date:"F j, o" }} and for ordering wine.

        You can always visit our site and <a href="{% url start_order party.id %}">order more wine</a> later or become a VIP by 
        <a href="{% url start_order party.id %}">subscribing</a> for our amazing wine selections.

        {% if custom_message %}
        {{ custom_message }}
        {% endif %}

        {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

        Your Tasteful Friends,

        - The Vinely Team

        """
        template = orm.ContentTemplate.objects.create(key="distribute_party_thanks_note_email", category=0)
        section = orm.Section.objects.create(category=0, content=content, template=template)
        variable, created = orm.Variable.objects.get_or_create(var="{{ party.title }}", description="The name of the party")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ party.event_date }}", description="Date when event took take place")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ custom_message }}", description="Optional custom message added to the thank you message")
        template.variables_legend.add(variable)

    def backwards(self, orm):
        "Write your backwards methods here."
        template = orm.ContentTemplate.objects.get(key="distribute_party_thanks_note_email", category=0)
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
