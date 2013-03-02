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

        Dear {{ pro_first_name }},

        Your host, {{ party.host.first_name }}, finished setting up the party below on <a href="http://{{ host_name }}">Vinely.com</a>.

        If they haven't yet, please make sure they order a Party Pack and track the RSVPs to ensure they have enough confirmed attendees.
        You can monitor the party details at: <a href="http://{{ host_name }}{% url party_details party.id %}">http://{{ host_name }}{% url party_details party.id %}</a>

        Party: "{{ party.title }}"

        Date: {{ party.event_date|date:"F j, o" }}

        Time: {{ party.event_date|date:"g:i A" }}

        Location: {{ party.address.full_text }}

        If you need to connect with {{ party.host.first_name }}, you can e-mail them at <a href="mailto:{{ party.host.email }}">{{ party.host.email }}</a>{% if host_phone %} or call them at {{ host_phone }}{% endif %}.

        {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

        Your Tasteful Friends,

        - The Vinely Team

        """

        template, created = orm.ContentTemplate.objects.get_or_create(key="party_setup_completed_email", category=0)
        section, created = orm.Section.objects.get_or_create(category=0, template=template)
        section.content = content
        section.save()

        variable, created = orm.Variable.objects.get_or_create(var="{{ pro_first_name }}", description="First name of the Vinely Pro")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ party.host.first_name }}", description="Name of the party host")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ party.title }}", description="Name of the party")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ party.event_date }}", description="Date of the event")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="http://{{ host_name }}{% url party_details party.id %}",
                                                        description="Link to party details page")
        template.variables_legend.add(variable)

    def backwards(self, orm):
        "Write your backwards methods here."
        template = orm.ContentTemplate.objects.get(key="party_setup_completed_email")
        orm.Section.objects.filter(template=template).delete()
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
