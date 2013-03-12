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

        Dear {{ pro_name }},

            Your host, {{ invite_host_name }}, is waiting for you to confirm the following party:

        Party: "{{ party.title }}"

        Date: {{ party.event_date|date:"F j, o" }}

        Time: {{ party.event_date|date:"g:i A" }}

        Location: {{ party.address.full_text }}

        {% if party.description %}Party Details: {{ party.description }}{% endif %}

        To confirm the party or make changes, click below:

        <a href="http://{{ host_name }}{% url party_details party.id %}">http://{{ host_name }}{% url party_details party.id %}</a>

        Remember that hosts can't send out their party invitation until you take the next step, so confirm their party now!

        If you need to connect with {{ invite_host_name }}, you can email them at <a href="mailto:{{ party.host.email }}">{{ party.host.email }}</a>{% if host_phone %} or call them at {{ host_phone }}{% endif %}.

        {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

        Your Tasteful Friends,

        - The Vinely Team

        """

        template = orm.ContentTemplate.objects.create(key="host_request_party_email", category=0)
        section = orm.Section.objects.create(category=0, template=template)
        section.content = content
        section.save()
        variable, created = orm.Variable.objects.get_or_create(var="{{ pro_name }}", description="Name of the Vinely Pro")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ invite_host_name }}", description="Name of the party host")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ party.host.email }}", description="The Host's email address")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ host_phone }}", description="The Host's phone number")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ party.title }}", description="The name of the party")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ party.event_date }}", description="Date when event took take place")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ party.address.full_text }}", description="Address of the event")
        template.variables_legend.add(variable)

        content = """

        Hey {{ invite_host_name }},

        We're thrilled about your interest in hosting a Vinely Taste Party!
        You have requested <b>{{ party.title }}</b> to be scheduled on <b>{{ party.event_date|date:"F j, o" }}</b> at <b>{{ party.event_date|date:"g:i A" }}</b>.

        {% if has_pro %}
            If any of these details are incorrect, don't worry, your Pro, {{ pro_name }}, can help you fix it.
            They can be contacted by email at <a href="mailto:{{ pro.email }}">{{ pro.email }}</a>{% if pro_phone %} or by phone at {{ pro_phone }}{% endif %}.
        {% else %}
            To ensure you'll be the host with the most, we'll need to pair you with a Vinely Pro.
            You will receive confirmation of this match via email within 48 hours.
            If any of these details are incorrect, don't worry, your Pro can help you fix it.
        {% endif %}

        Once your Pro confirms your party, your invitations can go out. Log in any time to see the status of your party or use the link below:

        <a href="http://{{ host_name }}{% url party_details party.id %}">http://{{ host_name }}{% url party_details party.id %}</a>

        If you have any questions, please contact a Vinely Care Specialist via e-mail at <a href="mailto:care@vinely.com">care@vinely.com</a> or by phone at 888-294-1128 ext. 1.

        We look forward to your party!

        {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

        Your Tasteful Friends,

            - The Vinely Team
        """

        template = orm.ContentTemplate.objects.create(key="new_party_scheduled_by_host_email", category=0)
        section = orm.Section.objects.create(category=0, template=template)
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
        variable, created = orm.Variable.objects.get_or_create(var="http://{{ host_name }}{% url party_details party.id %}",
                                                description="Link to party details page")
        template.variables_legend.add(variable)

    def backwards(self, orm):
        "Write your backwards methods here."
        template = orm.ContentTemplate.objects.get(key="host_request_party_email")
        orm.Section.objects.filter(template=template).delete()
        template.delete()

        template = orm.ContentTemplate.objects.get(key="new_party_scheduled_by_host_email")
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
