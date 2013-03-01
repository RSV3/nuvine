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
        Hi {{ taster_first_name }},

        {% if verification_code %}
        To allow you to enjoy all that Vinely has to offer, we have created a new account for you. Follow the following steps to activate your account.
        <h3>Activate Account:</h3>
        <table>
        <tr>
        <td>&nbsp;</td>
        <td><b>Step One</b></td>
        </tr>
        <tr>
        <td>&nbsp;</td>
        <td>Copy your temporary password: {{ temp_password }}</td>
        </tr>
        <tr>
        <td>&nbsp;</td>
        <td><b>Step Two</b></td>
        </tr>
        <tr>
        <td>&nbsp;</td>
        <td>Click the following <a href="http://{{ host_name }}{% url verify_account verification_code %}">link</a> and paste you temporary password to verify your account.</td>
        </tr>
        <tr>
        <td>&nbsp;</td>
        <td><a href="http://{{ host_name }}{% url verify_account verification_code %}">http://{{ host_name }}{% url verify_account verification_code %}</a></td>
        </tr>
        </table>
        {% endif %}

        {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

        Your Tasteful Friends,

        - The Vinely Team

        """
        template, created = orm.ContentTemplate.objects.get_or_create(key="welcome_email", category=0)
        section, created = orm.Section.objects.get_or_create(category=0, template=template)
        section.content = content
        section.save()

        variable, created = orm.Variable.objects.get_or_create(var="{{ taster_first_name }}", description="The taster's first name")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="{{ temp_password }}", description="Temporary password")
        template.variables_legend.add(variable)
        variable, created = orm.Variable.objects.get_or_create(var="http://{{ host_name }}{% url verify_account verification_code %}", description="Account verification link")
        template.variables_legend.add(variable)

    def backwards(self, orm):
        "Write your backwards methods here."
        template = orm.ContentTemplate.objects.get(key="welcome_email", category=0)
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
