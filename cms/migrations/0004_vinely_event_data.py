# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."

        general_content = """

        Join us October 10th, 2012 for a Vinely Taste Party open house from 4:00 pm to 7:00 pm in downtown Grand Rapids 
        at the <a href="http://www.shopmodiv.com/floorplan.html">Haworth|Interphase Showroom space</a> located on the 
        corner of Monroe Center and Division. 

        <h2>WHAT’S A VINELY TASTE PARTY?</h2>
        <p>Think of it as learning through drinking. It’s part wine tasting. Part personality test. And part...well...party.</p>

        <p>The wines you’ll sample will give us an idea of your personal taste. The flavors you enjoy and the ones you 
        could do without. After sipping, savoring, and rating each wine, we’ll assign you one of six Vinely Personalities. 
        Then, we’ll be able to send wines perfectly paired to your taste - right to your doorstep.</p>

        <p>Come early, stay late but promise you will come.</p>

        <p>Tell us you’ll attend! You know you want to!</p>

        <p>By filling out the information below, an online profile will be created for you and gets you one step closer to 
        finding out your Vinely Wine Personality.</p>
        <br />
        {% if fb_view %}
        <a class="btn btn-large btn-success" href="/facebook/event/signup/8/">Sign Me Up</a>
        {% else %}
        <a class="btn btn-large btn-success" href="/event/signup/8/">Sign Me Up</a>
        {% endif %}
        <br /><br />

        <h2>But where’s the parking?</h2>
        <p>Don’t let parking stand in your way. There are lots of meters, most of which are free after 6:00 pm. 
        If you arrive before 6:00 pm you can get an hour free in the Monroe Center lot located at 37 Ionia Avenue Northwest 
        (on the corner of Ionia ave and Louis)</p>
        <h2>Questions</h2>
        <p>Contact a Vinely Care Specialist at <a href="care@vinely.com">care@vinely.com</a> or call 1.888.294.1128 ext: 1</p>

        """
        template = orm.ContentTemplate.objects.create(key="vinely_event", category=1)
        orm.Section.objects.create(category=0, content=general_content, template=template)

    def backwards(self, orm):
        "Write your backwards methods here."
        template = orm.ContentTemplate.objects.get(key='vinely_event', category=1)
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
