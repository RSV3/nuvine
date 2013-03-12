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

        {{ custom_message }}

        {% if sig %}<div class="signature"><img src="{% static "img/vinely_logo_signature.png" %}"></div>{% endif %}

        {% if show_text_sig %}
        Tastefully,

        - {{ party.host.first_name }}
        {% endif %}
        """
        section = orm.Section.objects.get(template__key='distribute_party_thanks_note_email', category=0)
        section.content = content
        section.save()

    def backwards(self, orm):
        "Write your backwards methods here."

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
