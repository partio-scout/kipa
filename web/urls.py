from django.conf.urls.defaults import *
from tupa.models import *
from django.contrib import admin
admin.autodiscover()
from django.views.generic.simple import direct_to_template
from django.conf import settings

genericViews = patterns('django.views.generic.list_detail',
     (r'^tupa/$','object_list', {'template_name': 'tupa/index.html', 'queryset': Kisa.objects.all() } ),) 

media=patterns('django.views.static',
        (r'^kipamedia/(?P<path>.*)$', 'serve',
        {'document_root': settings.STATIC_DOC_ROOT}),)

urlpatterns = genericViews + media + patterns('web.tupa.views.',
     (r'^tupa/admin/(.*)', admin.site.root ),
     (r'^tupa/(?P<kisa_nimi>\w+)/tallenna/$', 'tallennaKisa'), 
     (r'^tupa/kantaan/$', 'tietokantaan'), 
     (r'^tupa/(?P<kisa_nimi>\w+)/$', 'kisa'),
     (r'^tupa/uusiKisa/maarita/$', 'maaritaKisa'),
     (r'^tupa/(?P<kisa_nimi>\w+)/maarita/$', 'maaritaKisa'),
     (r'^tupa/(?P<kisa_nimi>\w+)/maarita/tehtava/$', 'maaritaValitseTehtava'),
     (r'^tupa/(?P<kisa_nimi>\w+)/maarita/tehtava/uusi/sarja/(?P<sarja_id>\d+)/$', 'maaritaTehtava'),
     (r'^tupa/(?P<kisa_nimi>\w+)/maarita/tehtava/(?P<tehtava_id>\d+)/$', 'maaritaTehtava'),
     (r'^tupa/(?P<kisa_nimi>\w+)/maarita/vartiot/', 'maaritaVartiot'),
     (r'^tupa/(?P<kisa_nimi>\w+)/maarita/tehtava/kopioi/sarjaan/(?P<sarja_id>\d+)/$', 'kopioiTehtavia'),
     (r'^tupa/(?P<kisa_nimi>\w+)/syota/$', 'syotaKisa'),
     (r'^tupa/(?P<kisa_nimi>\w+)/syota/tehtava/(?P<tehtava_id>\d+)/$', 'syotaTehtava'),
     (r'^tupa/(?P<kisa_nimi>\w+)/tulosta/$', 'tulosta'),
     (r'^tupa/(?P<kisa_nimi>\w+)/tulosta/sarja/(?P<sarja_id>\d+)/$', 'tulostaSarja'),
     (r'^tupa/(?P<kisa_nimi>\w+)/tulosta/piirit/$', 'piirit'), )
