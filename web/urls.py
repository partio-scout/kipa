from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = [
        url(r'^kipa/',  include('tupa.urls')),
        url(r'^admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) #toimii vain kehityskäytössä

if settings.DEBUG :
        urlpatterns += [
                #url(r'^kipamedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
                ]

handler500 = 'tupa.views.raportti_500'
