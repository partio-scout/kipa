# coding: latin-1
from models import *
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect
import operator
from decimal import *
from django import newforms as forms
import django.template
from logger import lokkeri

import re
from formit import *

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

def maaritaValitseTehtava(request,kisa_nimi):
      sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
      sarjaTehtavat = []
      for s in sarjat :
           sarjanTehtavat = Tehtava.objects.filter(rasti__sarja = s )
           sarjaTehtavat.append( (s,sarjanTehtavat) )   
      return render_to_response('tupa/maaritaValitseTehtava.html', {'sarja_tehtavat': sarjaTehtavat })

def maaritaVartiot(request,kisa_nimi):
      sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
      sarjaVartiot=[]
      posti=None
      if request.method == 'POST':
          posti=request.POST
      for s in sarjat :
         vFormit=luoVartioFormit(s,posti,tyhjia=10)
         vartioFormit=[]
         for v in vFormit :
             v.save()
             if not v.empty() :
                 vartioFormit.append( v )
         sarjaVartiot.append( (s,vartioFormit) )
      return render_to_response('tupa/maaritaVartiot.html', { 'sarja_vartiot' : sarjaVartiot })

def maaritaTehtava(request, kisa_nimi, tehtava_id):
    tehtava = Tehtava.objects.filter(id=tehtava_id)[0]
    tehtavaForm = TehtavaForm(tehtava)
    maaritteet = SyoteMaarite.objects.filter( tehtava=tehtava )
    maariteFormit = []
    posti=None
    if request.method == 'POST':
          posti=request.POST
    maariteFormit=luoMaariteFormit(tehtava,posti,tyhjia=3)
    mFormit=[]
    for m in maariteFormit :
         m.save()
         if not m.empty() :
             mFormit.append(m)
   
    tehtavaForm = TehtavaForm(tehtava,posti)
    teht = Tehtava.objects.filter(id=tehtava_id)[0]
    if tehtavaForm.is_valid() :
       teht.nimi=tehtavaForm.clean_data['nimi']
       teht.kaava=tehtavaForm.clean_data['kaava']
       teht.save()

    return render_to_response('tupa/maarita_tehtava.html', { 'tehtava' : tehtava ,'tehtavaForm' : tehtavaForm , 'maariteFormit' : mFormit })

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
      tehtava = Tehtava.objects.filter(id=tehtava_id)[0]
      maaritteet = SyoteMaarite.objects.filter(tehtava=tehtava)
      vartiot = Vartio.objects.filter(sarja = tehtava.rasti.sarja )
      syoteFormit = []
      posti=None
      if request.method == 'POST':
          posti=request.POST

      for v in vartiot :
         rivi=[]
         for m in maaritteet :
              syotteet = Syote.objects.filter(vartio = v ).filter(maarite=m)
              syote=None
              if syotteet:
                  syote=syotteet[0]
              if m.tyyppi=="aika":
                  formi = AikaSyoteForm(m,v,posti)
                  if formi.is_valid() :
                     formi.save()
                     formi = AikaSyoteForm(m,v)
              elif m.tyyppi=="piste":
                  formi = PisteSyoteForm(m,v,posti)
                  if formi.is_valid() :
                     formi.save()
                     formi = PisteSyoteForm(m,v)
              
              rivi.append( formi )
         syoteFormit.append( (v,rivi))

      return render_to_response('tupa/syota_tehtava.html', 
             { 'tehtava' : tehtava ,
               'maaritteet' : maaritteet ,
               'syotteet' : syoteFormit } )

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

