import urllib2
import json
import feedparser
from time import strptime
from datetime import datetime
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
from open_facebook import exceptions as open_facebook_exceptions
from open_facebook.utils import send_warning
ITEMS_PER_PAGE = 10



def landing_page(request):

	context = RequestContext(request)
	return render_to_response('landing.html', context)



def recent_events_page(request,graph):

	me = graph('me')
	me = me['data']
	print me

	context = RequestContext(request)
	return render_to_response('profile.html', context)


@facebook_required_lazy
def profile_page(request,graph):
	#recent_events = Event.objects.order_by('-created')[:10]

	me = graph.get('me')
 	fid = me['id']
 	fid = int(fid)

 	#check if preferences for this user is saved
	pref = UserPref.objects.filter(f_id= fid).count()
	pref_ob = UserPref.objects.filter(f_id= fid)


	if pref == 0:
		#algorithm for suggestions
		me = graph.get('me')
		print me
		friends = graph.get('me/friends')
		music = graph.get('me/music')
		movies = graph.get('me/movies')
		tv = graph.get('me/television')

		try:
		    music_count = len(music['data'])
		except Exception as e:
		    music_count = 0

		try:
		    sports = len(me['sports'])
		except Exception as e:
		    sports = 0

		try:
		    lang_count = len(me['languages'])
		except Exception as e:
		    lang_count= 0


		#get counts for each
		music_count = len(music['data'])
		movie_count = len(movies['data'])
		tv_count = len(tv['data'])
		
		lang_count = 5*lang_count
		
		sports = 2*sports
		
		social_count = len(friends['data'])/20
		
		art_count = 2*tv_count + movie_count
		
		#debugging
		print "Sports"
		print sports
		print "Music" 
		print  music_count
		print "Art"
		print art_count
		print "Cultural"
		print lang_count
		print "Social"
		print social_count

		#retrieve primary and secondary prefs
		prefs = ["Sports", "Music", "Art", "Cultural", "Social"]
		prefs_num = [sports, music_count, art_count, lang_count, social_count]

		primary = prefs_num.index(max(prefs_num))
		pref1 = prefs[primary]

		prefs_num.remove(max(prefs_num))
		prefs.remove(pref1)

		secondary = prefs_num.index(max(prefs_num))
		pref2 = prefs[secondary]

		UserPref.objects.create(f_id = fid, primary = pref1, secondary = pref2)		

			
	else:
		name = "neel"
		


	#me = graph.get('me/television')
	#music = graph.get('me/music')
	#artists = music['data']
	#movies = graph.get('me/movies')
	#data = me['data']
	#print len(data)
	#print data
	
	
	#id = me['id']
	#friends = graph.get('me/friends')
	#data = friends['data']
	#for d in data:
	#	print d['name']
	#friends = graph.get('me/friends')
	#feed = graph.get('me/feed')
	#name = graph.get('me')['name']
	#print name

	#for n in name:
	#	print n['name']

	#recent_events = Event.objects.raw('SELECT "events_event"."id", "events_event"."created", "events_event"."title", "events_event"."description", "events_event"."location", "events_event"."host", "events_event"."date", "events_event"."male", "events_event"."female", "events_event"."facebook_link" FROM "events_event" ORDER BY "events_event"."created" DESC LIMIT 10')
	context = RequestContext(request)
	return render_to_response('profile.html', context)



def _event_save(request, form, graph):

			#retrieve host name
			#me = graph.get('me')
			#name = me['name']
			  

            # Create or get event.
            event, created = Event.objects.get_or_create(
              host = graph.get('me')['name'],
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


def event_save_page(request):
    if request.method == 'POST':
      form = EventSaveForm(request.POST)
      if form.is_valid():
          event = _event_save(request, form, graph)
          return HttpResponseRedirect(
                '/'
          )
    else:
      form = EventSaveForm()
      variables = RequestContext(request, {
      	'form': form
       })
    return render_to_response('event_save.html', variables)


def retrieve_events(request):
	return



def canopy_club_events(request):
	d = feedparser.parse('http://canopyclub.com/events/feed/')

	location = "The Canopy Club"

	#entries is list of all events from feed
	for entry in d.entries:
		title = entry['title']
		print title
		description = entry['description']
		link = entry['link']

	#url1 ='http://acm.uiuc.edu/calendar/feed.ics'
	#cal = urllib2.urlopen(url1).read()


def illinois_union_events(request):

	d = feedparser.parse('http://illinois.edu/calendar/rss/4061.xml')
	location = "Illinois Union"
	#entries is list of all events from feed
	for entry in d.entries:
		title = entry['title']
		description = entry['description']
		link = entry['link']
		date = entry['published']

		#manipulation to get date and time
		words = date.split()

		date =  words[2] + " " + words[1] + ", " + words[3]
		
		#retrieve and convert time from 24 hour to 12 hour clock
		time = words[4]
		d = datetime.strptime(time, "%H:%M:%S")
		time = d.strftime("%I:%M %p")

def lctc_film(request):

	d = feedparser.parse('http://illinois.edu/calendar/rss/4761.xml')
	location = "Foreign Language Building 1080"
	#entries is list of all events from feed
	for entry in d.entries:
		title = entry['title']
		description = entry['description']
		link = entry['link']
		date = entry['published']

		#manipulation to get date and time
		words = date.split()

		date =  words[2] + " " + words[1] + ", " + words[3]
		
		#retrieve and convert time from 24 hour to 12 hour clock
		time = words[4]
		d = datetime.strptime(time, "%H:%M:%S")
		time = d.strftime("%I:%M %p")
		


def krannert_events(request):

	url = 'http://www.krannertcenter.com/handlers/calendarjson.ashx'
	serialized_data = urllib2.urlopen(url).read()
	data = json.loads(serialized_data)

	count = 0

	#need to find way to retrieve json object name
	for date in data:

		#prints the day
		event_date = date

		#iterates over every item in day	
		for d in data[date]:


			#for every event print out it's title
			count = count + 1

			i_d = d['ID']
			title = d['Event']
			price = d['Price']
			description = d['Description']
			location = d['Location']
			time = d['Time']
			link = d['EventUrl']

			date = event_date.split();
			print date

			print strptime(date[1],'%b').tm_mon




			#can be used for event photos
			image_url = d['defaultimage']

			Event.objects.create(title = title, description = description, location = location, date = event_date, time = time)



	context = RequestContext(request)
	return render_to_response('landing.html', context)
























