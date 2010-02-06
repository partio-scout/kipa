from django.conf.urls.defaults import *
from models import *
from django.contrib import admin
admin.autodiscover()
from django.views.generic.simple import direct_to_template
from django.conf import settings

genericViews = patterns('django.views.generic.list_detail',        
                        (r'^$','object_list', 
                        {'template_name': 'tupa/index.html', 
                        'queryset': Kisa.objects.all() } ),) 

tal=r"(?P<talletettu>(talletettu)?)/?$"

urlpatterns = genericViews +  patterns('web.tupa.views',
        (r'^admin/(.*)', admin.site.root ),	
        (r'^apua/', 'apua'),
        (r'^post_txt/(?P<parametrit>.+)/$', 'post_txt'), 
        (r'^(?P<kisa_nimi>\w+)/tallenna/$', 'tallennaKisa'), 
        (r'^lisaaKisa/$', 'korvaaKisa'),
        (r'^(?P<kisa_nimi>\w+)/$', 'kisa'),
        (r'^uusiKisa/maarita/$', 'maaritaKisa'),
        (r'^(?P<kisa_nimi>\w+)/korvaa/$', 'korvaaKisa'),
        (r'^(?P<kisa_nimi>\w+)/poista/$', 'poistaKisa'),
        (r'^(?P<kisa_nimi>\w+)/maarita/'+tal, 'maaritaKisa'),
        (r'^(?P<kisa_nimi>\w+)/maarita/tehtava/$', 'maaritaValitseTehtava'),
        (r'^(?P<kisa_nimi>\w+)/maarita/tehtava/uusi/sarja/(?P<sarja_id>\d+)/$', 'maaritaTehtava'),
        (r'^(?P<kisa_nimi>\w+)/maarita/tehtava/(?P<tehtava_id>\d+)/'+tal , 'maaritaTehtava'),
        (r'^(?P<kisa_nimi>\w+)/maarita/vartiot/'+tal, 'maaritaVartiot'),
        (r'^(?P<kisa_nimi>\w+)/maarita/tehtava/kopioi/sarjaan/(?P<sarja_id>\d+)/$', 'kopioiTehtavia'),
        (r'^(?P<kisa_nimi>\w+)/maarita/testitulos/'+tal, 'testiTulos'),
        (r'^(?P<kisa_nimi>\w+)/luo/sarja/(?P<sarja_id>\d+)/testitulokset/$', 'luoTestiTulokset'),
        (r'^(?P<kisa_nimi>\w+)/maarita/tuomarineuvos/'+tal ,'tuomarineuvos'),
        (r'^(?P<kisa_nimi>\w+)/syota/(?P<tarkistus>(tarkistus/)?)$', 'syotaKisa'),
        (r'^(?P<kisa_nimi>\w+)/syota/(?P<tarkistus>(tarkistus/)?)tehtava/(?P<tehtava_id>\d+)/'+tal, 'syotaTehtava'),
        (r'^(?P<kisa_nimi>\w+)/tulosta/$', 'tulosta'),
        (r'^(?P<kisa_nimi>\w+)/tulosta/tilanne/$', 'laskennanTilanne'),
        (r'^(?P<kisa_nimi>\w+)/tulosta/sarja/(?P<sarja_id>\d+)/$', 'tulostaSarja'),
        (r'^(?P<kisa_nimi>\w+)/tulosta/sarja/tuloste/(?P<sarja_id>\d+)/$', 'tulostaSarjaHTML'),
        (r'^(?P<kisa_nimi>\w+)/tulosta/piirit/$', 'piirit'), 
        (r'^(?P<kisa_nimi>\w+)/login/$', 'loginSivu'), 
        (r'^(?P<kisa_nimi>\w+)/logout/$', 'logoutSivu'), )


if settings.DEBUG :
        urlpatterns += patterns('',
                (r'^kipamedia/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.STATIC_DOC_ROOT}),)

