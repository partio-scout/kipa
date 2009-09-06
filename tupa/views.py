# coding: latin-1
from models import *
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
import operator
from decimal import *
from django import forms
import django.template
from logger import lokkeri

import re
from formit import *
from TehtavanMaaritys import *
from duplicate import *

def kisa(request,kisa_nimi) :
        kisa = get_object_or_404(Kisa, nimi=kisa_nimi) 
        return render_to_response('tupa/kisa.html', {'kisa' : kisa })

def tulosta(request,kisa_nimi):
        sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
        return render_to_response('tupa/tulosta.html', {'sarja_list': sarjat })

def maaritaKisa(request, kisa_nimi=None):
        # Tietokantahaku:
        kisa = None
        if kisa_nimi:
                kisa = get_object_or_404(Kisa, nimi=kisa_nimi)
     
        # Post data
        posti=None
        if request.method == 'POST':
                posti=request.POST
        # Kisa formi
        kisaForm = KisaForm(posti,instance=kisa)
        if kisaForm.is_valid():
                kisa=kisaForm.save()
        
        # Sarja formset
        sarjaFormit=SarjaFormSet(posti,instance=kisa)
        if sarjaFormit.is_valid():
                sarjaFormit.save()
        sarjaFormit.label="Sarjat" 
        # Annetaan tiedot templatelle:
        if posti and sarjaFormit.is_valid() and kisaForm.is_valid() :
                return HttpResponseRedirect("/tupa/"+kisa.nimi+"/maarita/")
        else :
                return render_to_response('tupa/maarita.html', 
                                      { 'heading' : "Määrita Kisa" ,
                                      'taakse' : "../" ,
                                      'forms' : (kisaForm,) ,
                                      'formsets' : ( sarjaFormit,) })

def maaritaValitseTehtava(request,kisa_nimi):
        sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
        taulukko = []
        for s in sarjat :
                taulut = Tehtava.objects.filter(sarja = s )
                for taulu in taulut :
                        taulu.linkki = str(taulu.id)+"/"
                        taulu.nimi = unicode(taulu.jarjestysnro)+u" "+unicode(taulu.nimi)
                taulut.otsikko=s.nimi
                taulut.id=s.id
                taulukko.append(taulut)
        return render_to_response('tupa/maaritaValitseTehtava.html', 
                                        { 'taulukko' : taulukko,
                                        'heading' : "Valitse tehtävä",
                                        'taakse' : "/tupa/"+kisa_nimi+"/" })

def maaritaVartiot(request,kisa_nimi):
        sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
        sarjaVartiot=[]
        posti=None
        post_ok=True
        taulukko=[]
        if request.method == 'POST':
                posti=request.POST
        for s in sarjat :
                vartioFormit=VartioFormSet(posti,instance=s,prefix=s.nimi )
                if vartioFormit.is_valid():
                        vartioFormit.save() 
                else :
                        post_ok=False
                vartioFormit.otsikko=s.nimi
                vartioFormit.id=s.id
                taulukko.append( vartioFormit )
        if posti and post_ok:
                return HttpResponseRedirect("/tupa/"+kisa_nimi+"/maarita/vartiot/")
        else:
                return render_to_response('tupa/valitse_formset.html',
                                        { 'taulukko' : taulukko ,
                                        'heading' : "Määritä vartiot",
                                        'taakse' : "../../" })

def maaritaTehtava(request, kisa_nimi, tehtava_id=None, sarja_id=None):
        tehtava = None
        sarja = None
        if tehtava_id:
                tehtava=get_object_or_404(Tehtava, id=tehtava_id)
                sarja= tehtava.sarja
        else :
                sarja=get_object_or_404(Sarja, id=sarja_id)
         
        # Post Data
        posti=None
        if request.method == 'POST':
                posti=request.POST
        tehtavaForm = TehtavaForm( posti,instance=tehtava,sarja=sarja )
        if tehtavaForm.is_valid() :
                tehtava=tehtavaForm.save()
        taulukko=[]
        taulukko.append( tehtavaForm )
        tabit=[]
        for ot in tehtavaForm.osaTehtavaFormit:
                ot.otsikko=ot.instance.nimi
                ot.id=ot.instance.id
                tabit.append ("ot_tab_id_" + str(ot.instance.id) )
                taulukko.append(ot)

        if posti and tehtavaForm.is_valid() :
                return HttpResponseRedirect("/tupa/"+kisa_nimi+"/maarita/tehtava/"+str(tehtava.id)+'/' )
        else:
                return render_to_response('tupa/maarita.html', 
                                      { 'heading' : "Maarita Tehtava" ,
                                      'taakse' : "/tupa/"+kisa_nimi+"/maarita/tehtava" ,
                                      'forms' : taulukko,
                                      'tabs' : tabit,
                                      })

def syotaKisa(request, kisa_nimi):
        sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
        taulukko = []
        for s in sarjat :
                tehtavat = s.tehtava_set.all()
        for t in tehtavat:
                t.linkki = "tehtava/"+str(t.id)+"/" 
                tehtavat.id=s.id
                tehtavat.otsikko=s.nimi
                taulukko.append( tehtavat )
        return render_to_response('tupa/valitse_linkki.html', 
                                { 'taulukko' : taulukko,
                                'heading' : "Valitse tehtävä",
                                'taakse' : "../" })

def syotaTehtava(request, kisa_nimi , tehtava_id) :
        tehtava = Tehtava.objects.filter(id=tehtava_id)[0]
        maaritteet = SyoteMaarite.objects.filter(osa_tehtava__tehtava=tehtava)
        vartiot = Vartio.objects.filter(sarja = tehtava.sarja )
        syoteFormit = []
        posti=None
        if request.method == 'POST':
                posti=request.POST
        validi=True
        for v in vartiot :
                rivi=[]
                for m in maaritteet :
                        syotteet = Syote.objects.filter(vartio = v ).filter(maarite=m)
                        syote=None
                        formi=None
                        if syotteet:
                                syote=syotteet[0]
                        formi = SyoteForm(m,v,posti,instance=syote,prefix=v.nimi+str(m.pk),)
                        if formi.is_valid() :
                                formi.save()
                        else :
                                validi=False
                        rivi.append( formi )
                syoteFormit.append( (v,rivi))
        if posti and validi  :
                return HttpResponseRedirect("/tupa/"+kisa_nimi+"/syota/tehtava/"+str(tehtava.id)+'/' )
        else:
                return render_to_response('tupa/syota_tehtava.html', 
                        { 'tehtava' : tehtava ,
                        'maaritteet' : maaritteet ,
                        'syotteet' : syoteFormit } )

def testiTulos(request, kisa_nimi):
        taulukko=[]
        sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
        taulukko = []
        posti=None
        if request.method == 'POST':
                posti=request.POST
        
        
        for s in sarjat :
                taulut=s
                taulut.tiedot=Vartio.objects.filter(sarja=s)
                tehtavat=Tehtava.objects.filter(sarja = s )

                for v in taulut.tiedot:
                        v.tehtavat=tehtavat
                        v.formit=[]
                        for t in tehtavat:
                                formi=TestiTulosForm(posti,
                                                v,
                                                t,
                                                prefix=kisa_nimi+s.nimi+t.nimi+v.nimi)
                                if formi.is_valid():
                                        formi.save()
                                v.formit.append( formi )
                taulut.otsikko=s.nimi
                taulut.id=s.id
                taulukko.append(taulut)
        return render_to_response('tupa/testitulos.html',
                        { 'taulukko' : taulukko ,
                        'heading' : "Testi tuloksien määritys" ,
                        'taakse' : "../" })

def tulostaSarja(request, kisa_nimi, sarja_id) :
        sarja = Sarja.objects.get(id=sarja_id)
        lokkeri.clearLog()
        tulokset= sarja.laskeTulokset()
        return render_to_response('tupa/tulokset.html', {'tulos_taulukko' : tulokset }  )

def sarja(request,sarja_id) :
        sarja= Kisa.objects.get(id=sarja_id)
        return render_to_response('tupa/sarja.html', {'sarja_object': sarja })

def piirit(request,kisa_nimi) :
        return HttpResponse(kisa_nimi + " PIIRIN TULOSTUS" )

def kopioiTehtavia(request,kisa_nimi,sarja_id ):
        kisa =get_object_or_404(Kisa, nimi=kisa_nimi)
        sarjaan= get_object_or_404(Sarja, id=sarja_id)
        sarjat = Sarja.objects.filter(kisa=kisa)
        redirect=True
        posti=None
        if request.method == 'POST':
                posti=request.POST
        
        formit=[]
        for s in sarjat :
                vaiht = [] 
                tehtavat = Tehtava.objects.filter(sarja=s)
                for t in tehtavat:
                        vaiht.append( (t.id,t.nimi) )
                class KopioiForm(forms.Form):
                        kopioitavat_tehtavat = forms.MultipleChoiceField(choices=vaiht,
                                                                widget=forms.CheckboxSelectMultiple,
                                                                required=False)
                sarjaForm = KopioiForm(posti,prefix=s.nimi)
                formit.append(sarjaForm)
                sarjaForm.otsikko=s.nimi
                sarjaForm.id=s.id

                if posti and sarjaForm.is_valid():
                        kopioitavat = sarjaForm.cleaned_data['kopioitavat_tehtavat']
                        for k in kopioitavat:
                                tehtava= get_object_or_404(Tehtava, id=k)
                                kopioiTehtava(tehtava,sarjaan)
                else:
                        redirect=False
        if redirect:
                return HttpResponseRedirect("/tupa/"+kisa.nimi+"/maarita/tehtava/")
        else:
                return render_to_response('tupa/valitse_form.html', 
                                      { 'heading' : u"Kopioi Tehtavia sarjaan: "+sarjaan.nimi ,
                                      'taulukko' : formit ,
                                      'taakse' : "../../../../tehtava/" })

def tallennaKisa(request, kisa_nimi):
        """
        Palauttaa käyttäjälle valitun kisan xml formaatissa.
        Jättää henkilöt ja allergiat tallentamatta.
        """
        from django.core import serializers
        kisa = get_object_or_404(Kisa, nimi=kisa_nimi)
        objects=[kisa,]
        for s in kisa.sarja_set.all():
                objects.append(s)
                for v in s.vartio_set.all():
                        objects.append(v)
                for t in s.tehtava_set.all():
                        objects.append(t)
                        for te in t.testaustulos_set.all():
                                objects.append(te)
                        for tt in t.tuomarineuvostulos_set.all():
                                objects.append(tt)
                        for ot in t.osatehtava_set.all() :
                                for sm in ot.syotemaarite_set.all():
                                        objects.append(sm)
                                        for s in sm.syote_set.all():
                                                objects.append(s)
                                for p in ot.parametri_set.all():
                                        objects.append(p)
                                objects.append(ot)
        response = HttpResponse(serializers.serialize("xml", objects , indent=4), mimetype='application/xml')
        response['Content-Disposition'] = 'attachment; filename=tietokanta.xml'
        return response

def tietokantaan(request):
        """
        Palauttaa tupa tietokannan kokonaisuudessaan xml formaatissa käyttäjälle talletettavaksi.
        """
        from django.db.models import get_app, get_apps, get_models
        from django.core import serializers
        objects=[]
        for model in get_models(get_app("tupa")):
                objects.extend(model._default_manager.all())
        response = HttpResponse(serializers.serialize("xml", objects , indent=4), mimetype='application/xml')
        response['Content-Disposition'] = 'attachment; filename=tietokanta.xml'
        return response


