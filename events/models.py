from django.db import models
# Create your models here.

class Tag(models.Model):
    CATEGORY_CHOICES = (
    ('Music','Music'),
    ('Sports','Sports'),
    ('Tech','Tech'),
    ('Social','Social'),
    ('Cultural','Cultural'),
    ('Art','Art'),
    ('Health', 'Health')   
    )
    category = models.CharField(max_length = 100, choices=CATEGORY_CHOICES, default="Social")

    def __unicode__(self):
        return self.category



class Event(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    #mandatory attributes
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=300)
    date = models.DateField()
    time = models.CharField(max_length = 100)
    
    host = models.IntegerField(blank=True,null=True)
    price = models.CharField(max_length = 100, blank=True)
    male = models.IntegerField(default='0')
    female = models.IntegerField(default='0')
    
    event_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)

    tag = models.ManyToManyField(Tag,blank=True, null=True)

    def __unicode__(self):
        return self.title




class UserPref(models.Model):
    f_id = models.IntegerField()
    primary = models.CharField(max_length= 100)
    secondary = models.CharField(max_length = 100)

    def __unicode__(self): 
        return unicode(self.f_id)



class Going(models.Model):
    f_id = models.IntegerField()
    event_id = models.IntegerField()

    def __unicode__(self):
        return unicode(self.event_id)



