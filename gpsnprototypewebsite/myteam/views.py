from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    return HttpResponse("This is the homepage for the team attribute.")

def shareddata(request):
    return HttpResponse("Here will be all of the shared data within a team.")

def members(request):
    return HttpResponse("Here will list all of the team members.")
