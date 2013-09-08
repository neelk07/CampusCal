from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
# Create your views here.


def landing_page(request):
    context = RequestContext(request)
    return render_to_response('landing.html', context)
