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
        Your Vinely Party Request Has Been Submitted!

        Hey {{ party.host.first_name }},

        We're thrilled about your interest in hosting a Vinely Taste Party! You have requested <b>{{ party.title }}</b> to be scheduled on <b>{{ party.event_date|date:"F j, o" }}</b> at <b>{{ party.event_date|date:"g:i A" }}</b>.

        To ensure you'll be the host with the most, we'll need to pair you with a Vinely Pro. You will receive confirmation of this match via email within 48 hours. If any of these details are incorrect, don't worry, your Pro can help you fix it.

        Once your Pro confirms your party, your invitations can go out. Log in any time to see the status of your party or use the link below:

        <a href="http://{{ host_name }}{% url party_details party.id %}">http://{{ host_name }}{% url party_details party.id %}</a>

        If you have any questions, please contact a Vinely Care Specialist via e-mail at <a href="mailto:care@vinely.com">care@vinely.com</a> or by phone at 888-294-1128 ext. 1.

        We look forward to your party!

        Your Tasteful Friends,

        - The Vinely Team
        """
        template = orm.ContentTemplate.objects.create(key="new_party_scheduled_by_host_no_pro_email", category=0)
        section = orm.Section.objects.create(category=0, template=template)
        section.content = content
        section.save()
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
        template = orm.ContentTemplate.objects.get(key="new_party_scheduled_by_host_no_pro_email")
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
