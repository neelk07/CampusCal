import urllib2
import json
import feedparser
import itertools
from time import strptime, mktime
from datetime import datetime, timedelta
from django.shortcuts import render_to_response
from events.forms import *
from events.models import *
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.shortcuts import render_to_response, get_object_or_404
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

#For Paginator
ITEMS_PER_PAGE = 10



def landing_page(request):
	context = RequestContext(request)
	return render_to_response('landing.html', context)


@facebook_required_lazy
def recent_events_page(request, graph):

	me = graph.get('me')
 	fid = me['id']
 	fid = int(fid)

	#get events you are going to 
 	going_events = Going.objects.filter(f_id = fid)

 	#create list which will be populated with event ids
 	event_ids = []
 	
 	#add them to queryset of events you created
 	for event in going_events:
 		event_ids.append(event.event_id)

 	print event_ids

 	#retrievel date is today - 1 so that it will retrieve events from today also (some weird error)
	retrieve_date = datetime.now()
	retrieve_date = retrieve_date.replace(day = retrieve_date.day-1)

	#exclude events that are created by you
	recent_events = Event.objects.filter(date__gt=retrieve_date).order_by('-created').exclude(host = fid)

	#exclude events you are already going to
	recent_events = recent_events.exclude( id__in = event_ids)


	variables = RequestContext(request, {
      	'recent_events': recent_events})
	return render_to_response('recent_events.html', variables)	


@facebook_required_lazy
def profile_page(request,graph):

	me = graph.get('me')
 	fid = me['id']
 	fid = int(fid)

 	#retrieve events create by you
 	created_events = Event.objects.filter(host = fid)

 	#get events you are going to 
 	going_events = Going.objects.filter(f_id = fid)

 	my_events = Event.objects.none()
 	
 	#add them to queryset of events you created
 	for event in going_events:
 		my_events =  my_events | Event.objects.filter(id=event.event_id)

 	#retrievel date is today - 1 so that it will retrieve events from today also (some weird error)
	retrieve_date = datetime.now()
	retrieve_date = retrieve_date.replace(day = retrieve_date.day-1)

 	#only show events that have not happened yet
 	my_events = my_events.filter(date__gt = retrieve_date)
 	created_events = created_events.filter(date__gt = retrieve_date)

 	#check if preferences for this user is saved
	pref = UserPref.objects.filter(f_id= fid).count()

	if pref == 0:
		

################-------EVENT SUGGESTION ALGORITHM FROM FACEBOOK PROFILE------------#################
		
		me = graph.get('me')
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

		#retrieve primary and secondary prefs
		prefs = ["Sports", "Music", "Art", "Cultural", "Social"]
		prefs_num = [sports, music_count, art_count, lang_count, social_count]

		#now we calculate the first pref, remove it from list, and then calculate second pref
		primary = prefs_num.index(max(prefs_num))
		pref1 = prefs[primary]

		prefs_num.remove(max(prefs_num))
		prefs.remove(pref1)

		secondary = prefs_num.index(max(prefs_num))
		pref2 = prefs[secondary]

		UserPref.objects.create(f_id = fid, primary = pref1, secondary = pref2)		
			
	else:
		#we already have the pref object and now let's find the primary and secondary interest
		pref_ob = UserPref.objects.get(f_id= fid)
		pref1 = pref_ob.primary
		pref2 = pref_ob.secondary

	pref1 = (str)(pref1)
	pref2 = (str)(pref2)

	suggest_events_primary = Event.objects.filter(Q(tag__category__icontains = pref1))[:2]
	suggest_events_secondary = Event.objects.filter(Q(tag__category__icontains = pref2))[:2]
	suggest_events = itertools.chain(suggest_events_primary,suggest_events_secondary)
	
	variables = RequestContext(request, {
		'pref1': pref1,
		'pref2': pref2,
		'suggest_events' : suggest_events,
		'created_events' : created_events,
      	'my_events': my_events,
      	'fid': fid})

	return render_to_response('profile.html', variables)



@facebook_required_lazy
def event_save_page(request,graph):
    if request.method == 'POST':
      form = EventForm(request.POST)
      if form.is_valid():
        new_event = form.save()
        me = graph.get('me')
        fid = me['id']
        fid = int(fid)
        new_event.host = fid
        new_event.save()
        return HttpResponseRedirect('/profile/')
      else:
      	form = EventForm()
    else:
      form = EventForm()
      
    variables = RequestContext(request, {
      		'form': form})
    return render_to_response('event_save.html', variables)


@facebook_required_lazy
def update_event(request,id,graph):

	#check to make sure that you can't edit someone else's event
	me = graph.get('me')
 	fid = me['id']
 	fid = int(fid)
	event = Event.objects.get(id=id)
	if event.host != fid:
		return HttpResponseRedirect('/profile/')

	#otherwise let them update the event	
	form= EventForm(request.POST or None, instance=event)
	if request.method == 'POST':
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/profile/')
	variables = RequestContext(request, {
		'form': form
		})
	return render_to_response('event_save.html', variables)
    


@facebook_required_lazy
def delete_event(request,id,graph):
	#check to make sure that you can't delete someone else's event
	me = graph.get('me')
 	fid = me['id']
 	fid = int(fid)
	event = Event.objects.get(id=id)

	if event.host != fid:
		return HttpResponseRedirect('/profile/')

	event.delete()
	return HttpResponseRedirect('/profile/')



@facebook_required_lazy
def going_to_event(request,id,graph):

	me = graph.get('me')
 	fid = me['id']
 	fid = int(fid)

	#check if user is already going to event
	going = Going.objects.filter(f_id= fid, event_id = id)
	going_check = going.count()

	#if person is already going we change to not going by deleting the going entry in database
	if going_check == 1:
		going.delete()
		return HttpResponseRedirect('/profile/')

	#let's add it to database
	else:
		Going.objects.create(f_id = fid, event_id = id)
		return HttpResponseRedirect('/recent/')


@facebook_required_lazy
def search_events(request):
	form = SearchForm()
	events = Event.objects.all()
	tags = []
	query = None
	location = None
	date = None
	d = None
	tag = None
	price = None
	display_date = None

	show_results = False
	
	if 'title' in request.GET:
		show_results = True
		query = request.GET['title'].strip()
		if query:
			keywords = query.split()
			q = Q()
			for keyword in keywords:
				q = q & Q(title__icontains = keyword)
			form = SearchForm()
			events = Event.objects.filter(q)

	if 'location' in request.GET:
		location = request.GET['location']
		if location:
			events = events.filter(location__icontains = location)

	
	if 'date' in request.GET:
		date = request.GET['date']
		d = date
		if len(date) == 0:
			pass
		else:
			date = datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
			events = events.filter(date = date)

	if 'price' in request.GET:
		price = request.GET['price']
		if price:
			events = events.filter(price__lte = price)
		else:
			pass
	
	if 'tag' in request.GET:
		tag = request.GET['tag']
		if tag:
			events = events.filter(tag = tag)
		else:
			pass

	#implement algo for turning tag numbers into strings


	variables = RequestContext(request,{
		'query': query,
		'date':d,
		'price':price,
		'tag':tag,
		'form':form,
		'events': events,
		'show_results': show_results
		})

	return render_to_response('search.html', variables)

@facebook_required_lazy
def map_view(request,graph):

	me = graph.get('me')
 	fid = me['id']
 	fid = int(fid)

	#get events you are going to 
 	going_events = Going.objects.filter(f_id = fid)

 	#create list which will be populated with event ids
 	event_ids = []
 	
 	#add them to queryset of events you created
 	for event in going_events:
 		event_ids.append(event.event_id)

 	#retrievel date is today - 1 so that it will retrieve events from today also (some weird error)
	retrieve_date = datetime.now()
	retrieve_date = retrieve_date.replace(day = retrieve_date.day-1)

	#exclude events that are created by you
	recent_events = Event.objects.filter(date__gt=retrieve_date).order_by('-created').exclude(host = fid)[:5]
	variables = RequestContext(request,{
		'recent_events':recent_events,
		
		})

	return render_to_response('map_view.html', variables)



#####################------SCRAPERS FOR EVENT --------######################

def canopy_club_events(request):
	d = feedparser.parse('http://canopyclub.com/events/feed/')

	location = "The Canopy Club"
	loc = location.replace (" ", "+")
	url = 'http://maps.googleapis.com/maps/api/geocode/json?address='+loc+',+IL&sensor=true'
	serialized_data = urllib2.urlopen(url).read()
	data = json.loads(serialized_data)
	data = data['results']
	lat =  data[0]['geometry']['location']['lat']
	lng = data[0]['geometry']['location']['lng']

	#entries is list of all events from feed
	for entry in d.entries:
	
		title = entry['title']
		description = entry['description']
		link = entry['link']

		date = entry['ev_startdate']
		print title
		print description
		print link
		print date
		print lng 
		print lat
		break

	#url1 ='http://acm.uiuc.edu/calendar/feed.ics'
	#cal = urllib2.urlopen(url1).read()


def illinois_union_events(request):

	d = feedparser.parse('http://illinois.edu/calendar/rss/4061.xml')
	location = "Illini Union"
	loc = location.replace (" ", "+")
	url = 'http://maps.googleapis.com/maps/api/geocode/json?address='+loc+',+IL&sensor=true'
	serialized_data = urllib2.urlopen(url).read()
	data = json.loads(serialized_data)
	data = data['results']
	lat =  data[0]['geometry']['location']['lat']
	lng = data[0]['geometry']['location']['lng']

	#entries is list of all events from feed
	for entry in d.entries:
		title = entry['title']
		description = entry['description']
		link = entry['link']
		date = entry['published']
		date_list = entry['published_parsed']

		#manipulation to get date
		date_list = list(date_list)
		date_list = datetime(date_list[0],date_list[1],date_list[2])
		date_list = date_list.strftime('%Y-%m-%d')
		print date_list
		
		
		#retrieve and convert time from 24 hour to 12 hour clock and get time
		words = date.split()
		time = words[4]
		d = datetime.strptime(time, "%H:%M:%S")
		time = d.strftime("%I:%M %p")
		print time
		
		#check for duplicate entry
		repeat_event = Event.objects.filter(title = title, date = date_list, time = time).count()

		#no similar event was found so add it to the db
		if repeat_event == 0:
			event = Event.objects.create(title=title, description=description, location=location, lat= lat, lng = lng, time=time, date=date_list, event_url = link)
			tagged = Tag.objects.get(category = 'Social')
			event.tag.add(tagged)

def lctc_film(request):

	d = feedparser.parse('http://illinois.edu/calendar/rss/4761.xml')
	location = "Foreign Language Building 1080"
	loc = location.replace (" ", "+")
	url = 'http://maps.googleapis.com/maps/api/geocode/json?address='+loc+',+IL&sensor=true'
	serialized_data = urllib2.urlopen(url).read()
	data = json.loads(serialized_data)
	data = data['results']
	lat =  data[0]['geometry']['location']['lat']
	lng = data[0]['geometry']['location']['lng']
	#entries is list of all events from feed
	for entry in d.entries:
		title = entry['title']
		description = entry['description']
		link = entry['link']
		date = entry['published']
		date_list = entry['published_parsed']

		#manipulation to get date
		date_list = list(date_list)
		date_list = datetime(date_list[0],date_list[1],date_list[2])
		date_list = date_list.strftime('%Y-%m-%d')
			
		#retrieve and convert time from 24 hour to 12 hour clock and get time
		words = date.split()
		time = words[4]
		d = datetime.strptime(time, "%H:%M:%S")
		time = d.strftime("%I:%M %p")

		#check for duplicate entry
		repeat_event = Event.objects.filter(title = title, date = date_list, time = time).count()

		#no similar event was found so add it to the db
		if repeat_event == 0:
			event = Event.objects.create(title=title, description=description, location=location,lat = lat, lng = lng, time=time, date=date_list, event_url = link)
			tagged = Tag.objects.get(category='Cultural')
			event.tag.add(tagged)
			


def krannert_events(request):


	location = "Krannert Center For Performing Arts"

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
			if len(location) < 10:
				location = "Krannert Center For Performing Arts" + " - " + location
			loc = location.replace (" ", "+")
			url = 'http://maps.googleapis.com/maps/api/geocode/json?address='+loc+',+IL&sensor=true'
			serialized_data = urllib2.urlopen(url).read()
			dt = json.loads(serialized_data)
			if dt['status'] == 'OK':	
				dt = dt['results']
				lat =  dt[0]['geometry']['location']['lat']
				lng = dt[0]['geometry']['location']['lng']
			time = d['Time']
			link = d['EventUrl']

			date_list = event_date.split();
			date = datetime.strptime(date_list[1]+','+date_list[2]+date_list[3],"%B,%d,%Y")

			date = date.strftime('%Y-%m-%d')

			#can be used for event photos
			image_url = d['defaultimage']
			
			#check for duplicate entry
			repeat_event = Event.objects.filter(title = title, date = date, time = time).count()

			#no similar event was found so add it to the db
			if repeat_event == 0:
				event = Event.objects.create(title=title, description=description, location=location, lat = lat, lng = lng, time=time, date=date, price = price, event_url = link, image_url = image_url)
				tagged = Tag.objects.get(category='Music')
				event.tag.add(tagged)

	context = RequestContext(request)
	return render_to_response('landing.html', context)
























