from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
        (r'^kipa/',  include('tupa.urls')),
        (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG :
        urlpatterns += patterns('',
                (r'^kipamedia/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.STATIC_DOC_ROOT}),)

handler500 = 'tupa.views.raportti_500'
