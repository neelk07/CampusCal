import re
from django.contrib.auth.models import User
from django import forms
from django.core.files.images import get_image_dimensions
from events.models import *
from django.forms import ModelForm
from events.models import Event


class EventForm(ModelForm):
      class Meta:
            model = Event
            fields = ['title','description','location','date','time','price','event_url','image_url','tag']
