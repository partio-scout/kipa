# KiPa(KisaPalvelu), tuloslaskentajärjestelmä partiotaitokilpailuihin
#    Copyright url(C) 2010  Espoon Partiotuki ry. ept@partio.fi
# flake8: noqa

from django.conf.urls import *

from . import views

from .models import *

tal = r"(?P<talletettu>(talletettu)?)/?$"

urlpatterns = [
    url(r'^apua/', views.apua),
    url(r'^$', views.etusivu),
    url(r'^post_txt/(?P<parametrit>[^/]+)/$', views.post_txt),
    url(r'^(?P<kisa_nimi>[^/]+)/tallenna/$', views.tallennaKisa),
    url(r'^login/$', views.loginSivu),
    url(r'^logout/$', views.logoutSivu),
    url(r'^lisaaKisa/$', views.korvaaKisa),
    url(r'^(?P<kisa_nimi>[^/]+)/$', views.kisa),
    url(r'^uusiKisa/maarita/$', views.maaritaKisa),
    url(r'^(?P<kisa_nimi>[^/]+)/korvaa/$', views.korvaaKisa),
    url(r'^(?P<kisa_nimi>[^/]+)/poista/$', views.poistaKisa),
    url(r'^(?P<kisa_nimi>[^/]+)/maarita/'+tal, views.maaritaKisa),
    url(r'^(?P<kisa_nimi>[^/]+)/maarita/tehtava/$', views.maaritaValitseTehtava),
    url(r'^(?P<kisa_nimi>[^/]+)/maarita/tehtava/uusi/sarja/(?P<sarja_id>\d+)/$', views.maaritaTehtava),
    url(r'^(?P<kisa_nimi>[^/]+)/maarita/tehtava/(?P<tehtava_id>\d+)/'+tal, views.maaritaTehtava),
    url(r'^(?P<kisa_nimi>[^/]+)/maarita/vaiheet/(?P<tehtava_id>\d+)/(?P<vartio_id>\d*)/?', views.tehtavanVaiheet),
    url(r'^(?P<kisa_nimi>[^/]+)/maarita/vartiot/'+tal, views.maaritaVartiot),
    url(r'^(?P<kisa_nimi>[^/]+)/maarita/tehtava/kopioi/sarjaan/(?P<sarja_id>\d+)/$', views.kopioiTehtavia),
    url(r'^(?P<kisa_nimi>[^/]+)/maarita/testitulos/'+tal, views.testiTulos),
    url(r'^(?P<kisa_nimi>[^/]+)/luo/sarja/(?P<sarja_id>\d+)/testitulokset/$', views.luoTestiTulokset),
    url(r'^(?P<kisa_nimi>[^/]+)/maarita/tuomarineuvos/'+tal ,views.tuomarineuvos),
    url(r'^(?P<kisa_nimi>[^/]+)/syota/(?P<tarkistus>(tarkistus/)?)$', views.syotaKisa),
    url(r'^(?P<kisa_nimi>[^/]+)/syota/(?P<tarkistus>(tarkistus/)?)tehtava/(?P<tehtava_id>\d+)/'+tal, views.syotaTehtava),
    url(r'^(?P<kisa_nimi>[^/]+)/tulosta/normaali/$', views.tulosta),
    url(r'^(?P<kisa_nimi>[^/]+)/tulosta/normaali/sarja/(?P<sarja_id>\d+)/$', views.tulostaSarja),
    url(r'^(?P<kisa_nimi>[^/]+)/tulosta/tilanne/$', views.laskennanTilanne),
    url(r'^(?P<kisa_nimi>[^/]+)/tulosta/heijasta/sarja/(?P<sarja_id>\d+)/$', views.heijasta),
    url(r'^(?P<kisa_nimi>[^/]+)/tulosta/heijasta/$', views.heijasta),
    url(r'^(?P<kisa_nimi>[^/]+)/tulosta/tuloste/sarja/(?P<sarja_id>\d+)/$', views.tulostaSarjaHTML),
    url(r'^(?P<kisa_nimi>[^/]+)/tulosta/tuloste/$', views.tulosta),
    url(r'^(?P<kisa_nimi>[^/]+)/tulosta/csv/sarja/(?P<sarja_id>\d+)/$', views.sarjanTuloksetCSV),
    url(r'^(?P<kisa_nimi>[^/]+)/tulosta/csv/$', views.tulosta),
    url(r'^(?P<kisa_nimi>[^/]+)/tulosta/piirit/$', views.piirit),
]
