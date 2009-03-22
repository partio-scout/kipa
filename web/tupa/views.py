# coding: latin-1
from models import *
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect
import operator
import decimal 
from django.newforms import *
from django.forms import *
from django import oldforms
from django import newforms as forms
import django.template
from logger import lokkeri


def index(request):
      kisat = Kisa.objects.all()
      return render_to_response('tupa/index.html', {'latest_kisa_list': kisat })

def kisa(request,kisa_nimi) :
      return render_to_response('tupa/kisa.html', { })

def tulosta(request,kisa_nimi):
      sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
      return render_to_response('tupa/tulosta.html', {'sarja_list': sarjat })

def maaritaKisa(request, kisa_nimi):
      return HttpResponse("KISAN " + kisa_nimi + " MÄÄRITYS"  )

def maaritaTehtava(request, kisa_nimi, tehtava_id):
      return HttpResponse(kisan_nimi + " TEHTAVAN " + tehtava_id + " MÄÄRITYS")

def syotaKisa(request, kisa_nimi):
      sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
      taulukko = []
      for s in sarjat :
          rastit= s.rasti_set.all()
          rastin_tehtavat=[]
          for r in rastit :
              tehtavat=r.tehtava_set.all()
              for t in tehtavat:
                   rastin_tehtavat.append( t ) 
          taulukko.append( ( s ,rastin_tehtavat ) )
      print taulukko
      return render_to_response('tupa/syota_valitse_tehtava.html', { 'tehtava_taulukko' : taulukko } )

def syotaTehtava(request, kisa_nimi , tehtava_id) :
      return HttpResponse( kisa_nimi + " TEHTÄVÄN " + tehtava_id + " SYÖTTÖ")

def tulostaSarja(request, kisa_nimi, sarja_id) :
      sarja = Sarja.objects.filter(id=sarja_id)[0]
      lokkeri.clearLog()
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

#tulosten syotto rumalla tavalla
def lisaa_syote(request):

    SyoteForm = forms.models.form_for_model(Kisa)
    t = django.template.loader.get_template('tupa/syota666.html')
    c = None
    if request.method == 'POST':

        form = SyoteForm(request.POST)

        if form.is_valid():

            entry = form.save(commit=False)
            entry.owner = request.user
            entry.save()
            
            form = SyoteForm()
 
 
            c = Context({
            'form': form,
            })
            c.push()
            return HttpResponse(t.render(c))

    else:
        
        form = SyoteForm()
 
        c = Context({
        'form': form,
        })
    
    return HttpResponse(t.render(c))

