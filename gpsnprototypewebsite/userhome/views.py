from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return HttpResponse("This is the homepage for the user.")

def compare(request):
    return HttpResponse("This is where the HTML design to compare data will be displayed.")

def socialmedia(request):
    return HttpResponse("This is where users can check what people have recently posted on social media.")

def weather(request):
    return HttpResponse("This is where we can display current weather patterns.")

def visitors(request):
    return HttpResponse("This is where the numbers of visitors currently can be displayed.")

def results(request):
    return HttpResponse("Here will be the displays of the data comparison and conclusions.")