from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return HttpResponse("This is the homepage for the support attribute.")

def faqs(request):
    return HttpResponse("Put some FAQs here.")

def contact(request):
    return HttpResponse("This should be synced with About contacts.")