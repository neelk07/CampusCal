import re
from django.contrib.auth.models import User
from django import forms
from django.core.files.images import get_image_dimensions
from events.models import *


class EventSaveForm(forms.Form):
      
      title = forms.CharField(
      label=u'Title',
      widget=forms.TextInput(attrs={'size': 64})
      )
          
      description = forms.CharField(
      label=u'Description',
      widget = forms.Textarea(attrs={'size': 150})
      )

      location = forms.CharField(
      label=u'Location',
      widget=forms.TextInput(attrs={'size': 64})
      )

      time = forms.DateTimeField(
      label=u'Time and Date',
      required=True
      )
              
      tags = forms.CharField(
      label=u'Tags',
      required=False,
      widget=forms.TextInput(attrs={'size': 64})
      )
