from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    (r'wiki/', include('softwarefabrica.django.wiki.urls')),

    (r'^people/(?P<uname>\w+)$', 'people.views.detail'),
    (r'^people/(?P<uname>\w+)/?$', 'people.views.detail'),
    (r'^people/?$', 'people.views.index'),

    (r'^pub', 'people.views.publist'),

    (r'^api/graffiti/', include('sketch.urls')),

    (r'^stats/chart/(?P<key>[0-9a-zA-Z_]+)/$', 'stats.views.chart'),
    (r'^stats/flag/(?P<name>[0-9a-zA-Z_]+)/$', 'stats.views.flag'),
    (r'^stats/data/(?P<key>[0-9a-zA-Z_]+)/$', 'stats.views.stat_data'),
    (r'^stats/newflag/(?P<name>[0-9a-zA-Z_]+)/(?P<value>\d+)/(?P<stat_text>.*)/?$', 'stats.views.newflag'),
    (r'^stats/new/(?P<key>[0-9a-zA-Z_]+)/(?P<point>\d+\.?\d*)/$', 'stats.views.new'),
    (r'^stats/$', 'stats.views.index'),

    (r'^projects/twitter/', include('infolab.twitter.urls')),

    (r'^projects/', include('infolab.proj.urls')),


    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #(r'^admin/(.*)', admin.site.root),

    (r'^$', 'web.views.index'), # answers for everything

    url(r'^', include('basic.blog.urls')), # answers for everything
)
