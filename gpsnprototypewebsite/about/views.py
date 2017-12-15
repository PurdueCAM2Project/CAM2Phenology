from django.shortcuts import render

from django.http import HttpResponse
# Create your views here.

#this should be the "coming soon" page
def about(request):
    return HttpResponse("Here's what GPSN is all about.")

def contact(request):
    return HttpResponse("This view will be synced with the contact page in the support section.")

def mission(request):
    return HttpResponse("Here's what GPSN is all about.")

def abilities(request):
    return HttpResponse("What can the software do?")

def instructions(request):
    return HttpResponse("Here will be some instructions on how to use the software/site.")

def tutorial(request):
    return HttpResponse("Perhaps we can make a tutorial with steps to guide the user through the site.")