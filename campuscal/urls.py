from django.conf.urls import patterns, include, url
from events.views import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'campuscal.views.home', name='home'),
    # url(r'^campuscal/', include('campuscal.foo.urls')),

    url(r'^$', landing_page),
    url(r'^profile/$',profile_page),
    url(r'^recent/$',recent_events_page),
    url(r'^save/$', event_save_page),
    url(r'search/$',search_events),
    url(r'map/$', map_view),
    url(r'^event/update/(\d+)/$', update_event),
    url(r'^event/delete/(\d+)/$', delete_event),
    url(r'^event/going/(\d+)/$', going_to_event),
    url(r'^iue/$',illinois_union_events),
    url(r'^lctc/$',lctc_film),
    url(r'^kr/$',krannert_events),
    url(r'^cc/$',canopy_club_events),
    url(r'^ge/$',general_event),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^facebook/', include('django_facebook.urls')),
    url(r'^accounts/', include('django_facebook.auth_urls')), 

)
