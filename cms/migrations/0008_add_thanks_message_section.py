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
        Hi {{ taster_first_name }},

        {% if placed_order %}
        Thank you so much for attending my Vinely Taste Party and ordering some wine! I hope you had a great time and you and your personality are getting along great. Don't forget to rate your wines because the more you drink and rate, the better Vinely gets to know you!

        If you'd like to learn about hosting your own Vinely Party, feel free to reach out to our <a href="mailto:{{ pro_email }}">Pro</a> with any questions or to begin planning right away. Hosting has its perks..as a host, you will receive Vinely credit for each sale from your party!

        {% else %}
        Thank you so much for attending my Vinely Taste Party! I hope you had a fantastic time and you and your personality are getting along great!

        It is not too late to place an order. Just sign in at <a href="http://www.vinely.com">Vinely.com</a> to order a personalized selection of wine shipped right to your door. It's easy, convenient, delicious and best of all, guaranteed to please your taste buds!

        And if you join as a Vinely VIP you can enjoy new wines each month, with a continually improving selection based on your feedback ratings. Shipping is free, and you can cancel anytime.

        Remember, your satisfaction isn’t just a goal, it’s our guarantee!
        {% endif %}

        {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

        Tastefully,

        - {{ party.host.first_name }}

        """
        template = orm.ContentTemplate.objects.create(key="distribute_party_thanks_note_email", category=0)
        section, created = orm.Section.objects.get_or_create(category=0, content=content, template=template)
        variable, created = orm.Variable.objects.get_or_create(var="{{ party.title }}", description="The name of the party")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ party.event_date }}", description="Date when event took take place")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ custom_message }}", description="Optional custom message added to the thank you message")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ taster_first_name }}", description="The taster's first name")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ pro_email }}", description="The Vinely Pro's email address")
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
