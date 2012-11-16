# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

original_content = """

    {% load static %}

    What's a Vinely Party? Think of it as learning through drinking.  It's part wine tasting.
    Part personality test.  And part... well... party.

    The wines you'll sample will give us an idea of your personal taste. The flavors you enjoy and the ones you could do without. After sipping, savoring, and rating each wine, we'll assign you one of six Vinely Personalities. Then, we'll be able to send wines perfectly paired to your taste - right to your doorstep.

      Party: "{{ party.title }}"
      Host: {{ invite_host_name }} <{{ invite_host_email }}>
      {% if party.description %}{{ party.description }}{% endif %}
      Date: {{ party.event_date|date:"F j, o" }}
      Time: {{ party.event_date|date:"g:i A" }}
      Location: {{ party.address.full_text }}

    {% if verification_code %}
    To manage your invitation and follow the party, we have created a new account for you.

    Copy this verification code: {{ temp_password }} and click the following link

      http://{{ host_name }}{% url verify_account verification_code %}

    to verify your e-mail address and create a new password.
    {% endif %}

    {% if custom_message %}
    {{ custom_message }}
    {% endif %}

    Will you attend? You know you want to! RSVP by {{ rsvp_date|date:"F j, o" }}. Better yet, don't wait!

    {% if plain %}
    Click on this link to RSVP Now: http://{{ host_name }}{% url party_rsvp party.id %}
    {% else %}
    <div class="email-rsvp-button"><a href="http://{{ host_name }}{% url party_rsvp party.id %}">RSVP Now</a></div>
    {% endif %}

    {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

    Your Tasteful Friends,

    - The Vinely Team

    """


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."
        content = """

        {% load static %}

        What's a Vinely Party? Think of it as learning through drinking.  It's part wine tasting.
        Part personality test.  And part... well... party.

        The wines you'll sample will give us an idea of your personal taste. The flavors you enjoy and the ones you could do without. After sipping, savoring, and rating each wine, we'll assign you one of six Vinely Personalities. Then, we'll be able to send wines perfectly paired to your taste - right to your doorstep.

          Party: "{{ party.title }}"
          Host: {{ invite_host_name }} <{{ invite_host_email }}>
          {% if party.description %}{{ party.description }}{% endif %}
          Date: {{ party.event_date|date:"F j, o" }}
          Time: {{ party.event_date|date:"g:i A" }}
          Location: {{ party.address.full_text }}

        {% if verification_code %}
        To manage your invitation and follow the party, we have created a new account for you.

        Copy this verification code: {{ temp_password }} and click the following link

          http://{{ host_name }}{% url verify_account verification_code %}

        to verify your e-mail address and create a new password.
        {% endif %}

        {% if custom_message %}
        {{ custom_message }}
        {% endif %}

        Will you attend? You know you want to! RSVP by {{ rsvp_date|date:"F j, o" }}. Better yet, don't wait!

        {% if plain %}
        Click on this link to RSVP Now: http://{{ host_name }}{% url party_rsvp rsvp_code party.id %}
        {% else %}
        <div class="email-rsvp-button"><a href="http://{{ host_name }}{% url party_rsvp rsvp_code party.id %}">RSVP Now</a></div>
        {% endif %}

        {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

        Your Tasteful Friends,

        - The Vinely Team

        """
        template = orm['cms.ContentTemplate'].objects.get(key="distribute_party_invites_email", category=0)
        section = orm['cms.Section'].objects.get(category=0, template=template)
        section.content = content
        section.save()
        variable, created = orm['cms.Variable'].objects.get_or_create(var="{{ rsvp_code }}", description="Unique RSVP code for each user")
        template.variables_legend.add(variable)

    def backwards(self, orm):
        "Write your backwards methods here."
        template = orm['cms.ContentTemplate'].objects.get(key="distribute_party_invites_email", category=0)
        section = orm['cms.Section'].objects.get(category=0, template=template)
        section.content = original_content
        section.save()
        variable = orm['cms.Variable'].objects.get(var="{{ rsvp_code }}", description="Unique RSVP code for each user")
        template.variables_legend.remove(variable)

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
