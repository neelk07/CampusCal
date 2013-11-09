from django.db import models
# Create your models here.

class Tag(models.Model):
    CATEGORY_CHOICES = (
    ('M','Music'),
    ('S', 'Sports'),
    ('T', 'Tech'),
    ('SO', 'Social'),
    ('C', 'Cultural'),
    ('A', 'Art'),
    ('H', 'Health')   
    )
    category = models.CharField(max_length = 100, choices=CATEGORY_CHOICES, default="Social")

    def __unicode__(self):
        return self.name



class Event(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    #mandatory attributes
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=300)
    date = models.DateField()
    time = models.TimeField()
    host = models.IntegerField()

    price = models.IntegerField(blank=True)
    male = models.IntegerField(default='0')
    female = models.IntegerField(default='0')
    
    event_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)

    tag = models.ManyToManyField(Tag,blank=True, null=True)

    def __unicode__(self):
        return self.title


class UserPref(models.Model):
    f_id = models.IntegerField()
    tag = models.ManyToManyField(Tag,blank=True, null=True)

    def __unicode__(self): 
        return self.f_id


class Going(models.Model):
    f_id = models.IntegerField()
    event_id = models.IntegerField()

    def __unicode__(self):
        return self.event_id



