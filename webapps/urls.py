from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
	url(r'^$', 'socialnetwork.views.redirect'),
    url(r'^socialnetwork/', include('socialnetwork.urls')),
)


