from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from events.models import *
# Create your views here.


def landing_page(request):
    context = RequestContext(request)
    return render_to_response('landing.html', context)


def top_events_page(request):
	top_events = Event.objects.order_by('-created')[:10]
	variables = RequestContext(request,
		{
			'top_events':top_events
		})
	return render_to_response('top_events.html',variables)