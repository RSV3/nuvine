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

        We are so excited that you want to host a Vinely Taste Party!

        You have already set up your account. Your login is {{ host.email }}.

        The next step, if you haven't done so already, is to schedule the details of your party.
        Your process is complete when you submit your party for approval by your Vinely Pro.
        (Don't worry if you don't have a Vinely Pro yet, we will find you the perfect Pro to ensure your are the host with the most!).

        Once your pro confirms your party, the invitation will be sent to attendees you have added.
        In the meantime, if you have any questions you can always contact a Vinely Care Specialist at (888)294-1128 ext. 1 or email us at <a href="mailto:care@vinely.com">care@vinely.com</a>.

        PS - Please add <a href="mailto:info@vinely.com">info@vinely.com</a> to your address book to ensure our emails get through!

        {% if sig %}<div class="signature"><img src="{{ EMAIL_STATIC_URL }}img/vinely_logo_signature.png"></div>{% endif %}

        Your Tasteful Friends,

        - The Vinely Team

        """
        template = orm.ContentTemplate.objects.create(key="signed_up_as_host_email", category=0)
        section, created = orm.Section.objects.create(category=0, template=template, content=content)
        variable, created = orm.Variable.objects.get_or_create(var="{{ host.email }}", description="The Host's email address")
        template.variables_legend.add(variable)

    def backwards(self, orm):
        "Write your backwards methods here."

        template = orm.ContentTemplate.objects.get(key="signed_up_as_host_email")
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
