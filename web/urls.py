from django.conf.urls.defaults import *

urlpatterns = patterns('web.tupa.views.',
     (r'^tupa/$', 'index'),
     (r'^tupa/admin/', include('django.contrib.admin.urls')),
     (r'^tupa/(?P<kisa_nimi>\w+)/$', 'kisa'),
     (r'^tupa/(?P<kisa_nimi>\w+)/maarita/$', 'maaritaKisa'),
     (r'^tupa/(?P<kisa_nimi>\w+)/maarita/tehtava/(?P<tehtava_id>\d+)/$', 'maaritaTehtava'),
     (r'^tupa/(?P<kisa_nimi>\w+)/syota/$', 'syotaKisa'),
     (r'^tupa/(?P<kisa_nimi>\w+)/syota/tehtava/(?P<tehtava_id>\d+)/$', 'syotaTehtava'),
     (r'^tupa/(?P<kisa_nimi>\w+)/tulosta/sarja/(?P<sarja_id>\d+)/$', 'tulostaSarja'),
     (r'^tupa/(?P<kisa_nimi>\w+)/tulosta/piirit/$', 'piirit'),
)
     #(r'^tupa/(?P<kisa_id>\d+)/$', 'web.tupa.views.kisa'),
     # (r'^tupa/(?P<kisa_id>\d+)/(?P<sarja_id>\d+)/$', 'web.tupa.views.sarja'),
     #(r'^tupa/tulokset/(?P<sarja_id>\d+)/$', 'web.tupa.views.tulokset'),
     #(r'^tupa/syotto/$', 'web.tupa.views.syotto'),
