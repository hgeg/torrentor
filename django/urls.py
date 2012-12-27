from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^torrentor/', include('foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    url(r'^$', 'downloader.views.pre_upload', name='form'),
    url(r'^form/$', 'downloader.views.pre_upload', name='form'),
    url(r'^upload/$', 'downloader.views.upload', name='upload'),
    url(r'^newslog/$', 'downloader.views.newslog', name='newslog'),
    url(r'^check/(?P<type>.*)/(?P<query>.*)/$', 'downloader.views.check', name='check'),
    url(r'^perform/(?P<action>.*)/(?P<pid>.*)/$', 'downloader.views.perform', name='perform'),
    url(r'^convert/(?P<key>.*)/$', 'downloader.views.convert', name='convert'),
    url(r'^search/(?P<path>.*)/$', 'downloader.views.search', name='search'),
    url(r'^search/$', 'downloader.views.search', name='search'),
    url(r'^subs/(?P<path>.*)/$', 'downloader.views.subtitles', name='subtitles'),
    url(r'^browse/(?P<path>.*)/page:(?P<page>.*)/$', 'downloader.views.browse', name='browse'),
    url(r'^browse/(?P<path>.*)/$', 'downloader.views.browse', name='browse'),
    url(r'^browse/$', 'downloader.views.browse', name='browse'),
    url(r'^files/(?P<path>.*)$', 'django.views.static.serve',{'document_root':'/home/can/torrentor/public/files/'}),
)
