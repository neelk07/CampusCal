import re
from django.contrib.auth.models import User
from django import forms
from datetime import datetime
from django.forms.util import ErrorList
from django.core.files.images import get_image_dimensions
from events.models import *
from django.forms import ModelForm
from events.models import Event


class EventForm(ModelForm):
      class Meta:
            model = Event
            fields = ['title','description','location','date','time','price','event_url','image_url','tag']

      #def clean_date(self):
      #  if 'date' in self.cleaned_data:
      #      date = self.cleaned_data['date']
      #      now = datetime.now()
      #      now = now.date()
      #      if date < now:
      #            raise forms.ValidationError('Please Provide A Date in the Future!')


class SearchForm(forms.Form):
      query = forms.CharField(
        label=u'Search For An Event',
        widget=forms.TextInput(attrs={'size': 32})
        )

            