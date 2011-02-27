from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^account/(?P<screen_name>[a-z0-9_]+)/(?P<plot_type>\w+)/$',
        'twitter.views.account'),
    (r'^powerlaw/(?P<plot_type>\w+)/(?P<dt>\d+\-\d+\-\d+)/$',
        'twitter.views.powerlaw'),
    (r'^powerlaw/(?P<plot_type>\w+)/(?P<dt>\d+\-\d+\-\d+)/(?P<maxnum>\d*)/$',
        'twitter.views.powerlaw'),
    (r'^powercen/(?P<plot_type>\w+)/(?P<dt>\d+\-\d+\-\d+)/$',
        'twitter.views.powercentrality'),
    (r'^powercen/(?P<plot_type>\w+)/(?P<dt>\d+\-\d+\-\d+)/(?P<maxnum>\d*)/$',
        'twitter.views.powercentrality'),
)
