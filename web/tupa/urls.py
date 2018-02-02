# encoding: utf-8
# KiPa(KisaPalvelu), tuloslaskentajärjestelmä partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi


from django.conf.urls import url
from django.conf import settings
from . import views


tal=r"(?P<talletettu>(talletettu)?)/?$"

urlpatterns = [
        url(r'^apua/', views.apua, name='apua'),
        url(r'^$', views.etusivu, name='etusivu'),
        url(r'^post_txt/(?P<parametrit>[^/]+)/$', views.post_txt, name='post_txt'), 
        url(r'^(?P<kisa_nimi>[^/]+)/tallenna/$', views.tallennaKisa, name='tallennaKisa'), 
        url(r'^login/$', views.loginSivu, name='loginSivu'), 
        url(r'^logout/$', views.logoutSivu, name='logoutSivu'),
        url(r'^lisaaKisa/$', views.korvaaKisa, name='korvaaKisa'),
        url(r'^(?P<kisa_nimi>[^/]+)/$', views.kisa, name='kisa'),
        url(r'^uusiKisa/maarita/$', views.maaritaKisa, name='maaritaKisa'),
        url(r'^(?P<kisa_nimi>[^/]+)/korvaa/$', views.korvaaKisa, name='korvaaKisa'),
        url(r'^(?P<kisa_nimi>[^/]+)/poista/$', views.poistaKisa, name='poistaKisa'),
        url(r'^(?P<kisa_nimi>[^/]+)/maarita/'+tal, views.maaritaKisa, name='maaritaKisa'),
        url(r'^(?P<kisa_nimi>[^/]+)/maarita/tehtava/$', views.maaritaValitseTehtava, name='maaritaValitseTehtava'),
        url(r'^(?P<kisa_nimi>[^/]+)/maarita/tehtava/uusi/sarja/(?P<sarja_id>\d+)/$', views.maaritaTehtava, name='maaritaTehtava'),
        url(r'^(?P<kisa_nimi>[^/]+)/maarita/tehtava/(?P<tehtava_id>\d+)/'+tal , views.maaritaTehtava, name='maaritaTehtava'),
        url(r'^(?P<kisa_nimi>[^/]+)/maarita/vaiheet/(?P<tehtava_id>\d+)/(?P<vartio_id>\d*)/?' ,  views.tehtavanVaiheet, name='tehtavanVaiheet'),
        url(r'^(?P<kisa_nimi>[^/]+)/maarita/vartiot/'+tal,  views.maaritaVartiot, name='maaritaVartiot'),
        url(r'^(?P<kisa_nimi>[^/]+)/maarita/tehtava/kopioi/sarjaan/(?P<sarja_id>\d+)/$', views.kopioiTehtavia, name='kopioiTehtavia'),
        url(r'^(?P<kisa_nimi>[^/]+)/maarita/testitulos/'+tal, views.testiTulos, name='testiTulos'),
        url(r'^(?P<kisa_nimi>[^/]+)/luo/sarja/(?P<sarja_id>\d+)/testitulokset/$', views.luoTestiTulokset, name='luoTestiTulokset'),
        url(r'^(?P<kisa_nimi>[^/]+)/maarita/tuomarineuvos/'+tal , views.tuomarineuvos, name='tuomarineuvos'),
        url(r'^(?P<kisa_nimi>[^/]+)/syota/(?P<tarkistus>(tarkistus/)?)$', views.syotaKisa, name='syotaKisa'),
        url(r'^(?P<kisa_nimi>[^/]+)/syota/(?P<tarkistus>(tarkistus/)?)tehtava/(?P<tehtava_id>\d+)/'+tal, views.syotaTehtava, name='syotaTehtava'),
        url(r'^(?P<kisa_nimi>[^/]+)/tulosta/normaali/$', views.tulosta, name='tulosta'),
        url(r'^(?P<kisa_nimi>[^/]+)/tulosta/normaali/sarja/(?P<sarja_id>\d+)/$', views.tulostaSarja, name='tulostaSarja'),
        url(r'^(?P<kisa_nimi>[^/]+)/tulosta/tilanne/$', views.laskennanTilanne, name='laskennanTilanne'),
        url(r'^(?P<kisa_nimi>[^/]+)/tulosta/heijasta/sarja/(?P<sarja_id>\d+)/$', views.heijasta, name='heijasta'),
        url(r'^(?P<kisa_nimi>[^/]+)/tulosta/heijasta/$', views.heijasta, name='heijasta'),
        url(r'^(?P<kisa_nimi>[^/]+)/tulosta/tuloste/sarja/(?P<sarja_id>\d+)/$', views.tulostaSarjaHTML, name='tulostaSarjaHTML'),
        url(r'^(?P<kisa_nimi>[^/]+)/tulosta/tuloste/$', views.tulosta, name='tulosta'),
        url(r'^(?P<kisa_nimi>[^/]+)/tulosta/csv/sarja/(?P<sarja_id>\d+)/$', views.sarjanTuloksetCSV, name='sarjanTuloksetCSV'),
        url(r'^(?P<kisa_nimi>[^/]+)/tulosta/csv/$', views.tulosta, name='tulosta'),
        url(r'^(?P<kisa_nimi>[^/]+)/tulosta/(?P<muotoilu>[^/]+)/piirit/$', views.piirinTulokset, name='piirit'),
        ]

