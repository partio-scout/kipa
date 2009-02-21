from django.conf.urls.defaults import *

urlpatterns = patterns('',
     (r'^tupa/$', 'web.tupa.views.index'),
     (r'^tupa/(?P<kisa_id>\d+)/$', 'web.tupa.views.kisa'),
     (r'^tupa/(?P<kisa_id>\d+)/(?P<sarja_id>\d+)/$', 'web.tupa.views.sarja'),
     (r'^tupa/tulokset/(?P<sarja_id>\d+)/$', 'web.tupa.views.tulokset'),
     (r'^tupa/syotto/$', 'web.tupa.views.syotto'),
     (r'^tupa/admin/', include('django.contrib.admin.urls')),
)
