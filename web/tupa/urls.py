# encoding: utf-8
# KiPa(KisaPalvelu), tuloslaskentajärjestelmä partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi


from django.conf.urls.defaults import *
from models import *
from django.contrib import admin
admin.autodiscover()
from django.views.generic.simple import direct_to_template
from django.views.generic.simple import redirect_to
from django.conf import settings


tal=r"(?P<talletettu>(talletettu)?)/?$"

urlpatterns = patterns('tupa.views',
        #(r'^admin/', include(admin.site.urls) ),	
        (r'^apua/', 'apua'),
        (r'^$', 'etusivu'),
        (r'^post_txt/(?P<parametrit>[^/]+)/$', 'post_txt'), 
        (r'^(?P<kisa_nimi>[^/]+)/tallenna/$', 'tallennaKisa'), 
        (r'^login/$', 'loginSivu'), 
        (r'^logout/$', 'logoutSivu'),
        (r'^lisaaKisa/$', 'korvaaKisa'),
        (r'^(?P<kisa_nimi>[^/]+)/$', 'kisa'),
        (r'^uusiKisa/maarita/$', 'maaritaKisa'),
        (r'^(?P<kisa_nimi>[^/]+)/korvaa/$', 'korvaaKisa'),
        (r'^(?P<kisa_nimi>[^/]+)/poista/$', 'poistaKisa'),
        (r'^(?P<kisa_nimi>[^/]+)/maarita/'+tal, 'maaritaKisa'),
        (r'^(?P<kisa_nimi>[^/]+)/maarita/tehtava/$', 'maaritaValitseTehtava'),
        (r'^(?P<kisa_nimi>[^/]+)/maarita/tehtava/uusi/sarja/(?P<sarja_id>\d+)/$', 'maaritaTehtava'),
        (r'^(?P<kisa_nimi>[^/]+)/maarita/tehtava/(?P<tehtava_id>\d+)/'+tal , 'maaritaTehtava'),
        (r'^(?P<kisa_nimi>[^/]+)/maarita/vartiot/'+tal, 'maaritaVartiot'),
        (r'^(?P<kisa_nimi>[^/]+)/maarita/tehtava/kopioi/sarjaan/(?P<sarja_id>\d+)/$', 'kopioiTehtavia'),
        (r'^(?P<kisa_nimi>[^/]+)/maarita/testitulos/'+tal, 'testiTulos'),
        (r'^(?P<kisa_nimi>[^/]+)/luo/sarja/(?P<sarja_id>\d+)/testitulokset/$', 'luoTestiTulokset'),
        (r'^(?P<kisa_nimi>[^/]+)/maarita/tuomarineuvos/'+tal ,'tuomarineuvos'),
        (r'^(?P<kisa_nimi>[^/]+)/syota/(?P<tarkistus>(tarkistus/)?)$', 'syotaKisa'),
        (r'^(?P<kisa_nimi>[^/]+)/syota/(?P<tarkistus>(tarkistus/)?)tehtava/(?P<tehtava_id>\d+)/'+tal, 'syotaTehtava'),
        (r'^(?P<kisa_nimi>[^/]+)/tulosta/$', 'tulosta'),
        (r'^(?P<kisa_nimi>[^/]+)/tulosta/tilanne/$', 'laskennanTilanne'),
        (r'^(?P<kisa_nimi>[^/]+)/heijasta/sarja/$', 'elavaTulos'),
		(r'^(?P<kisa_nimi>[^/]+)/heijasta/sarja/(?P<sarja_id>\d+)/$', 'elavaTulos'),
		(r'^(?P<kisa_nimi>[^/]+)/tulosta/sarja/(?P<sarja_id>\d+)/$', 'tulostaSarja'),
        (r'^(?P<kisa_nimi>[^/]+)/tulosta/sarja/tuloste/(?P<sarja_id>\d+)/$', 'tulostaSarjaHTML'),
        (r'^(?P<kisa_nimi>[^/]+)/tulosta/sarja/csv/(?P<sarja_id>\d+)/$', 'sarjanTuloksetCSV'),
        (r'^(?P<kisa_nimi>[^/]+)/tulosta/piirit/$', 'piirit'), 
        )

if settings.DEBUG :
        urlpatterns += patterns('',
                (r'^kipamedia/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.STATIC_DOC_ROOT}),)

