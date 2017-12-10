from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name = 'home'),
    url(r'^faqs/$', views.faqs, name = 'faqs'),
    url(r'^contact/$', views.contact, name = 'contact'), # this should be synced with About contact


]