from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
        (r'^tupa/',  include('web.tupa.urls')),
)

if settings.DEBUG :
        urlpatterns += patterns('',
                (r'^kipamedia/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.STATIC_DOC_ROOT}),)

handler500 = 'tupa.views.raportti_500'
