from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    mycontext = {
        'data': 'Welcome to Global Phenology'
    }

    return render(request,'video_app/video.html', mycontext)