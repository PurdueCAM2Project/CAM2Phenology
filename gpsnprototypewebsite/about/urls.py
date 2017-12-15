from django.conf.urls import url #imports necessary stuff to handle URL confs and such

from . import views #get the views from the folder that you're in

urlpatterns = [
    url(r'^$', views.about, name = 'about'),
    url(r'^contact/$', views.contact, name = 'contact'), # needs to be synced with Support Contact
    url(r'^mission/$', views.mission, name = 'mission'),
    url(r'^abilities/$', views.abilities, name = 'abilities'),
    url(r'^instructions/$', views.instructions, name = 'instructions'),
    url(r'^instructions/tutorial/$', views.tutorial, name = 'tutorial'),


]