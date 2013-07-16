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
    name = models.CharField(max_length=120, blank=True)
    key = models.CharField(max_length=128, unique=True)
    active = models.BooleanField(default=True)
    #content = models.TextField()
    category = models.IntegerField(choices=TEMPLATE_TYPE)
    variables_legend = models.ManyToManyField(Variable)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', '-key']


class Section(models.Model):
    SECTION_TYPE = (
        (0, 'General Section'),
        (1, 'Taster Section'),
        (2, 'Host Section'),
        (3, 'Pro Section'),
        (4, 'Header Section'),
        (5, 'Sub Heading Section'),
    )
    key = models.CharField(max_length=128, db_index=True)
    # category = models.IntegerField(choices=SECTION_TYPE, default=0)
    content = models.TextField()
    template = models.ForeignKey(ContentTemplate, related_name='sections')

    def __unicode__(self):
        return self.key.title()
