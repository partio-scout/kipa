from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('web.tupa.views.',
     (r'^tupa/$', 'index'),
     (r'^tupa/admin/(.*)', admin.site.root ),
     (r'^tupa/(?P<kisa_nimi>\w+)/$', 'kisa'),
     (r'^tupa/(?P<kisa_nimi>\w+)/maarita/$', 'maaritaKisa'),
     (r'^tupa/(?P<kisa_nimi>\w+)/maarita/tehtava/$', 'maaritaValitseTehtava'),
     (r'^tupa/(?P<kisa_nimi>\w+)/maarita/tehtava/uusi/sarja/(?P<sarja_id>\d+)/$', 'maaritaTehtava'),
     (r'^tupa/(?P<kisa_nimi>\w+)/maarita/tehtava/(?P<tehtava_id>\d+)/$', 'maaritaTehtava'),
     (r'^tupa/(?P<kisa_nimi>\w+)/maarita/vartiot/', 'maaritaVartiot'),
     (r'^tupa/(?P<kisa_nimi>\w+)/syota/$', 'syotaKisa'),
     (r'^tupa/(?P<kisa_nimi>\w+)/syota/tehtava/(?P<tehtava_id>\d+)/$', 'syotaTehtava'),
     (r'^tupa/(?P<kisa_nimi>\w+)/tulosta/$', 'tulosta'),
     (r'^tupa/(?P<kisa_nimi>\w+)/tulosta/sarja/(?P<sarja_id>\d+)/$', 'tulostaSarja'),
     (r'^tupa/(?P<kisa_nimi>\w+)/tulosta/piirit/$', 'piirit'),
)
