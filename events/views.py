from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from events.forms import *
from events.models import *
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.shortcuts import render_to_response, get_object_or_404
from datetime import datetime, timedelta
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage
from django_facebook import exceptions as facebook_exceptions, \
    settings as facebook_settings
from django_facebook.connect import CONNECT_ACTIONS, connect_user
from django_facebook.decorators import facebook_required_lazy
from django_facebook.utils import next_redirect, get_registration_backend, \
    to_bool, error_next_redirect, get_instance_for
ITEMS_PER_PAGE = 10



def landing_page(request):
    context = RequestContext(request)
    return render_to_response('landing.html', context)
    

@facebook_required_lazy
def recent_events_page(request):
	#recent_events = Event.objects.order_by('-created')[:10]
	recent_events = Event.objects.raw('SELECT "events_event"."id", "events_event"."created", "events_event"."title", "events_event"."description", "events_event"."location", "events_event"."host", "events_event"."date", "events_event"."male", "events_event"."female", "events_event"."facebook_link" FROM "events_event" ORDER BY "events_event"."created" DESC LIMIT 10')
	variables = RequestContext(request,
		{
			'recent_events':recent_events
		})
	return render_to_response('recent_events.html',variables)



def _event_save(request, form):
            
			#retreive host 
			

            # Create or get event.
            event, created = Event.objects.get_or_create(
              title = form.cleaned_data['title'],
              description = form.cleaned_data['description'],
              location = form.cleaned_data['location'],
              time = form.cleaned_data['time']
            )
            # Update event title
          
            # Update event description.
            
            # Update event date
            
            # If the event is being updated, clear old tag list.
            if not created:
              event.tag_set.clear()
            # Create new tag list.
            tag_names = form.cleaned_data['tags'].split()
            for tag_name in tag_names:
                tag, dummy = Tag.objects.get_or_create(name=tag_name)
                event.tag_set.add(tag)

          
            # Save event to database.
            event.save()
            return event