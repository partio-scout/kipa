from django.conf.urls import url

from . import views

urlpatterns = [
        url(r'^(?P<kisa_nimi>[^/]+)/kayttajat/$', views.kayttajat, name='kayttajat'),
        url(r'^kayttaja/(?P<user_name>[^/]+)/$', views.kayttajan_tiedot, name='kayttaja'),
]
