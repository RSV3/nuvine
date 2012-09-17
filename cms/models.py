from django.db import models

# Create your models here.

class Variable(models.Model):
  var = models.CharField(max_length=128) 
  description = models.CharField(max_length=128)

class ContentTemplate(models.Model):
	TEMPLATE_TYPE = (
		(0, 'Email Template'),
		(1, 'Web Template'),
	)

	key = models.CharField(max_length=128)
	content = models.TextField()
	category = models.IntegerField(choices=TEMPLATE_TYPE)
	variables_legend = models.ManyToManyField(Variable)  
	last_modified = models.DateTimeField(auto_now=True)
