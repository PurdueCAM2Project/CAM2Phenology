from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("This is the index page of signing in?")

def login(request):
    return HttpResponse("This is where users will log in.")

def signup(request):
    return HttpResponse("This is where users will sign up.")