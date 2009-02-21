# coding: latin-1
from models import *
from django.shortcuts import render_to_response
import operator
import decimal 

def index(request):
      kisat = Kisa.objects.all()
      return render_to_response('tupa/index.html', {'latest_kisa_list': kisat })

def kisa(request,kisa_id):
      sarjat = Sarja.objects.filter(kisa__id=kisa_id)
      return render_to_response('tupa/kisa.html', {'sarja_list': sarjat })

def sarja(request,sarja_id) :
      sarja= Kisa.objects.filter(id=sarja_id)[0]
      return render_to_response('tupa/sarja.html', {'sarja_object': sarja })

def tulokset(request,sarja_id):
    sarja = Sarja.objects.filter(id=sarja_id)[0]
    tulokset= sarja.laskeTulokset()
    print tulokset[0][0].nimi
    return render_to_response('tupa/tulokset2.html', {'tulos_taulukko' : tulokset }  )


