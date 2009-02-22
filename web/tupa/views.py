# coding: latin-1
from models import *
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect
import operator
import decimal 
from django.newforms import *
import django.forms

def index(request):
      kisat = Kisa.objects.all()
      return render_to_response('tupa/index.html', {'latest_kisa_list': kisat })

def kisa(request,kisa_nimi):
      sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
      return render_to_response('tupa/kisa.html', {'sarja_list': sarjat })

def maaritaKisa(request, kisa_nimi):
      return HttpResponse("KISAN " + kisan_nimi + " MÄÄRITYS"  )

def maaritaTehtava(request, kisa_nimi, tehtava_id):
      return HttpResponse(kisan_nimi + " TEHTAVAN " + tehtava_id + " MÄÄRITYS")

def syotaKisa(request, kisa_nimi):
      return HttpResponse("KISAN " + kisa_nimi + " SYÖTTÖ")

def syotaTehtava(request, kisa_nimi , tehtava_id) :
      return HttpResponse( kisa_nimi + " TEHTÄVÄN " + tehtava_id + " SYÖTTÖ")

def tulostaSarja(request, kisa_nimi, sarja_id) :
      sarja = Sarja.objects.filter(id=sarja_id)[0]
      tulokset= sarja.laskeTulokset()
      return render_to_response('tupa/tulokset2.html', {'tulos_taulukko' : tulokset }  )

def sarja(request,sarja_id) :
      sarja= Kisa.objects.filter(id=sarja_id)[0]
      return render_to_response('tupa/sarja.html', {'sarja_object': sarja })

def piirit(request,kisa_nimi) :
      return HttpResponse(kisa_nimi + " PIIRIN TULOSTUS" )

#tulosten syotto  
def syotto(request,sarja_id):
    request.POST["pisteet"]
    return render_to_response('tupa/syotto.html', {})

