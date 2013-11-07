from django.db import models
# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name



class Event(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=300)
    host = models.CharField(max_length=200)
    date = models.DateTimeField()
    male = models.IntegerField(default='0')
    female = models.IntegerField(default='0')
    link = models.URLField(blank=True)
    tag = models.ManyToManyField(Tag,blank=True, null=True)

    def __unicode__(self):
        return self.title






