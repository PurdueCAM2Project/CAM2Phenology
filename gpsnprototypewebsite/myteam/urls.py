from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name = 'home'),
    url(r'^shareddata/$', views.shareddata, name = 'shareddata'),
    url(r'^members/$', views.members, name = 'members'),


]