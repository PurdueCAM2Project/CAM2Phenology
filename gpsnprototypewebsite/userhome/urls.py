from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name = 'home'),
    url(r'^compare/$', views.compare, name = 'compare'),
    url(r'^compare/results/$', views.results, name = 'results'),
    url(r'^socialmedia/$', views.socialmedia, name = 'socialmedia'),
    url(r'^weather/$', views.weather, name = 'weather'),
    url(r'^visitors/$', views.visitors, name = 'visitors'),


]