from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url('^$', views.index),
    url('^stream$', views.stream),
    url('^memory$', views.memory),
)
