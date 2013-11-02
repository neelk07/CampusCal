from django.db import models
# Create your models here.


class Event(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=300)
    host = models.CharField(max_length=200)
    date = models.DateTimeField()
    male = models.IntegerField(default='0')
    female = models.IntegerField(default='0')
    facebook_link = models.URLField(blank=True)

    def __unicode__(self):
        return self.title





