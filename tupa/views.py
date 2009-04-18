# coding: latin-1
from models import *
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import operator
from decimal import *
from django import forms
import django.template
from logger import lokkeri

import re
from formit import *

def index(request):
      kisat = Kisa.objects.all()
      return render_to_response('tupa/index.html', {'latest_kisa_list': kisat })

def kisa(request,kisa_nimi) :
      kisat = Kisa.objects.filter(nimi=kisa_nimi)
      kisa=None
      if kisat:
          kisa = kisat[0]
      if kisa:  
          return render_to_response('tupa/kisa.html', {'kisa' : kisa })
      else :
          return HttpResponseRedirect(reverse('web.tupa.views.index'))

def tulosta(request,kisa_nimi):
      sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
      return render_to_response('tupa/tulosta.html', {'sarja_list': sarjat })

def maaritaKisa(request, kisa_nimi):
     kisat=Kisa.objects.filter(nimi=kisa_nimi)
     kisa=None
     id=None
     if kisat:
         kisa=kisat[0]
         id=kisa.id
     posti=None
     if request.method == 'POST':
          posti=request.POST
     
     # Luodaan Kisa formi
     kisaForm = KisaForm(posti,instance=kisa)
     if kisaForm.is_valid():
         kisa=kisaForm.save()
    
     # Luodaan Sarja formi
     sarjaFormit=[]
     
     sFormit=luoSarjaFormit(kisa,posti,tyhjia=4)

     if sFormit.is_valid():
         instances = sFormit.save(commit=False) 
         for instance in instances:
             instance.kisa=kisa
             instance.save()
          
     if request.method == 'POST' and sFormit.is_valid():
         return HttpResponseRedirect(reverse('web.tupa.views.maaritaKisa', args=(kisa.nimi,)))
     else :
         return render_to_response('tupa/maaritaKisa.html', { 'kisa_form' : kisaForm, 'sarja_formit' : sFormit })

def maaritaValitseTehtava(request,kisa_nimi):
      sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
      sarjaTehtavat = []
      for s in sarjat :
           sarjanTehtavat = Tehtava.objects.filter(sarja = s )
           sarjaTehtavat.append( (s,sarjanTehtavat) )   
      return render_to_response('tupa/maaritaValitseTehtava.html', {'sarja_tehtavat': sarjaTehtavat })

def maaritaVartiot(request,kisa_nimi):
      sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
      sarjaVartiot=[]
      posti=None
      post_ok=True
      if request.method == 'POST':
          posti=request.POST
      for s in sarjat :
         vFormit=luoVartioFormit(s,posti,tyhjia=10)
         if vFormit.is_valid():
             instances = vFormit.save(commit=False) 
             for instance in instances:
                 instance.sarja=s
                 instance.save()
         else :
             post_ok=False
         sarjaVartiot.append( (s,vFormit) )
      if posti and post_ok:
         return HttpResponseRedirect(reverse('web.tupa.views.maaritaVartiot', args=(kisa_nimi,)))
      else:
         return render_to_response('tupa/maaritaVartiot.html', { 'sarja_vartiot' : sarjaVartiot })
"""
def maaritaUusiTehtava(request, kisa_nimi, sarja_id) :
        kisa = get_object_or_404(Kisa, nimi=kisa_nimi)
        sarja = get_object_or_404(Sarja, id=sarja_id)
        tehtavaForm = TehtavaForm()
        tehtava=None
        maariteFormit = luoMaariteFormit(tyhjia=5)
        if request.method == 'POST':
             tehtavaForm = TehtavaForm(request.POST)
             tehtava = tehtavaForm.save(commit=False)
             tehtava.sarja=sarja
             tehtava.save()        

             if tehtava:
                 maariteFormit = luoMaariteFormit(tehtava,request.POST,tyhjia=5)
                 if maariteFormit.is_valid() : 
                    instances = maariteFormit.save(commit=False) 
                    for instance in instances:
                        instance.tehtava=tehtava
                        instance.save()
                 return HttpResponseRedirect(reverse('web.tupa.views.maaritaTehtava', 
                                                args=(kisa_nimi,tehtava.id )))
        
        return render_to_response('tupa/maarita_tehtava.html', 
                                            { 'tehtava' : tehtava ,
                                            'tehtavaForm' : tehtavaForm , 
                                            'maariteFormit' : maariteFormit })

"""


def maaritaTehtava(request, kisa_nimi, tehtava_id=None, sarja_id=None):
    tehtava = None
    sarja = None
    if tehtava_id:
         tehtava=get_object_or_404(Tehtava, id=tehtava_id)
         sarja= tehtava.sarja
    else :
         sarja=get_object_or_404(Sarja, id=sarja_id)

    posti=None
    if request.method == 'POST':
          posti=request.POST
    # Tehtävä
    tehtavaForm = TehtavaForm( posti,instance=tehtava )
    if tehtavaForm.is_valid() :
       tehtava=tehtavaForm.save(commit=False)
       tehtava.sarja=sarja
       tehtava.save()

    # Määritteet
    maariteFormit=luoMaariteFormit(tehtava,posti,tyhjia=3)
    if maariteFormit.is_valid() :
         instances = maariteFormit.save(commit=False) 
         for instance in instances:
             instance.tehtava=tehtava
             instance.save()
    maariteFormit=luoMaariteFormit(tehtava,tyhjia=3)

    # Osapisteiden kaavat:
    """kaavaFormit = luoKaavaFormit(tehtava,posti,tyhjia=3)
    if kaavaFormit.is_valid() :
         kaavat = kaavaFormit.save(commit=False)
         for kaava in kaavat: 
             kaava.tehtava=tehtava
             kaava.save()
    """
    kaavaFormit=None

    if posti and tehtavaForm.is_valid() :
       return HttpResponseRedirect("/tupa/"+kisa_nimi+"/maarita/tehtava/"+str(tehtava.id)+'/' )
    else:
       return render_to_response('tupa/maarita_tehtava.html', { 'tehtava' : tehtava ,'tehtavaForm' : tehtavaForm , 'maariteFormit' : maariteFormit , 'kaavaFormit' : kaavaFormit })

def syotaKisa(request, kisa_nimi):
      sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
      taulukko = []
      for s in sarjat :
          tehtavat = s.tehtava_set.all()
          taulukko.append( ( s ,tehtavat) )
      print taulukko
      return render_to_response('tupa/syota_valitse_tehtava.html', { 'tehtava_taulukko' : taulukko } )

def syotaTehtava(request, kisa_nimi , tehtava_id) :
      tehtava = Tehtava.objects.filter(id=tehtava_id)[0]
      maaritteet = SyoteMaarite.objects.filter(tehtava=tehtava)
      vartiot = Vartio.objects.filter(sarja = tehtava.sarja )
      syoteFormit = []
      posti=None
      if request.method == 'POST':
          posti=request.POST

      for v in vartiot :
         rivi=[]
         for m in maaritteet :
              syotteet = Syote.objects.filter(vartio = v ).filter(maarite=m)
              syote=None
              formi=None
              if syotteet:
                  syote=syotteet[0]
              if m.tyyppi=="aika":
                  formi = AikaSyoteForm(m,v,posti)
                  if formi.is_valid() :
                     formi.save()
                     formi = AikaSyoteForm(m,v)
              elif m.tyyppi=="piste":
                  formi = PisteSyoteForm(posti,instance=syote)
                  if formi.is_valid() :
                     formi.save()
              
              rivi.append( formi )
         syoteFormit.append( (v,rivi))

      return render_to_response('tupa/syota_tehtava.html', 
             { 'tehtava' : tehtava ,
               'maaritteet' : maaritteet ,
               'syotteet' : syoteFormit } )

def tulostaSarja(request, kisa_nimi, sarja_id) :
      sarja = Sarja.objects.get(id=sarja_id)
      lokkeri.clearLog()
      tulokset= sarja.laskeTulokset()
      return render_to_response('tupa/tulokset2.html', {'tulos_taulukko' : tulokset }  )

def sarja(request,sarja_id) :
      sarja= Kisa.objects.get(id=sarja_id)
      return render_to_response('tupa/sarja.html', {'sarja_object': sarja })

def piirit(request,kisa_nimi) :
      return HttpResponse(kisa_nimi + " PIIRIN TULOSTUS" )

