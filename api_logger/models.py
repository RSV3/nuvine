from django.db import models
from django.contrib.auth.models import User


class APILog(models.Model):
    user = models.ForeignKey(User, null=True)
    source = models.CharField(max_length=12)
    method = models.CharField(max_length=6)
    uri = models.CharField(max_length=64)
    request_data = models.TextField(blank=True)
    response_data = models.TextField(blank=True)
    status = models.PositiveIntegerField(default=200)
    created = models.DateTimeField(auto_now_add=True)

    @models.permalink
    def get_absolute_url(self):
        return ('api_logger:log_detail', [self.id])
