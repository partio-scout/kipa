# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
import operator
from decimal import *
from django import forms
import django.template
from django.utils.safestring import SafeUnicode

from duplicate import kopioiTehtava
from duplicate import kisa_xml
import random

from models import *
import re
from formit import *
from TehtavanMaaritys import *

def tehtavanTilanne(tehtava):
        vartioita=len( tehtava.sarja.vartio_set.all() )
        syotteita=len( Syote.objects.filter(maarite__osa_tehtava__tehtava=tehtava) )
        maaritteita=len( SyoteMaarite.objects.filter(osa_tehtava__tehtava=tehtava) )
        tila="a"
        if syotteita: tila="o"
        if syotteita==vartioita*maaritteita : tila="s"
        if tehtava.tarkistettu : tila="t"
        return tila

def kisa(request,kisa_nimi) :
        """
        Kisakohtainen päävalikko.
        """
        kisa = get_object_or_404(Kisa, nimi=kisa_nimi) 
        return render_to_response('tupa/kisa.html', {'kisa' : kisa })

def tulosta(request,kisa_nimi):
        """
        Valintalista kisan sarjojen tuloksista.
        """
        sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
        return render_to_response('tupa/tulosta.html', {'sarja_list': sarjat, 'kisa_nimi': kisa_nimi })

def maaritaKisa(request, kisa_nimi=None,talletettu=None):
        """
        Kisan ja sarjojen määritys.
        """
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
        kisaForm.label="Kisan perustiedot"
        if kisaForm.is_valid():
                kisa=kisaForm.save()
        
        # Sarja formset
        sarjaFormit=SarjaFormSet(posti,instance=kisa)
        if sarjaFormit.is_valid():
                sarjaFormit.save()
        sarjaFormit.label="Sarjat" 
        # Annetaan tiedot templatelle:
        if posti and sarjaFormit.is_valid() and kisaForm.is_valid() :
                return HttpResponseRedirect("/tupa/"+kisa.nimi+"/maarita/talletettu/")
        else :
                tal=""
                if talletettu=="talletettu" and not posti : tal="Talletettu!"
                taakse= "/tupa/"
                if kisa_nimi : taakse = "/tupa/"+kisa_nimi+"/"
                return render_to_response('tupa/maarita.html', 
                                      { 'heading' : "Määritä kisa" ,
                                      'taakse' : taakse ,
                                      'forms' : (kisaForm,) ,
                                      'formsets' : ( sarjaFormit,),
                                      'kisa_nimi' : kisa_nimi,
                                      'talletettu': tal })

def maaritaValitseTehtava(request,kisa_nimi):
        """
        Valitsee tehtävän määritettäväksi.
        """
        # Post data
        posti=None
        if request.method == 'POST':
                posti=request.POST

        sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
        taulukko = []
        for s in sarjat :
                formsetti = TehtavaLinkkilistaFormset(posti, 
                                queryset=Tehtava.objects.filter(sarja = s ),
                                prefix="sarja_"+str(s.id)+"_" )
                formsetti.otsikko=s.nimi
                formsetti.id=s.id

                if posti and formsetti.is_valid():
                        formsetti.save()
                else :
                        taulukko.append(formsetti)
        
        if posti :
                return HttpResponseRedirect("/tupa/"+kisa_nimi+"/maarita/tehtava/")
        else:
                return render_to_response('tupa/maaritaValitseTehtava.html', 
                                        { 'taulukko' : taulukko,
                                        'heading' : "Valitse tehtävä",
                                        'taakse' : "/tupa/"+kisa_nimi+"/" })

def maaritaVartiot(request,kisa_nimi,talletettu=None):
        """
        Määrittää kisan vartiot sarjoittain.
        """
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
                return HttpResponseRedirect("/tupa/"+kisa_nimi+"/maarita/vartiot/talletettu/")
        else:
                tal=""
                if talletettu=="talletettu" and not posti : tal="Talletettu!"

                return render_to_response('tupa/valitse_formset.html',
                                        { 'taulukko' : taulukko ,
                                        'heading' : "Määritä vartiot",
                                        'taakse' : "/tupa/"+kisa_nimi+"/",
                                        'talletettu': tal })

def maaritaTehtava(request, kisa_nimi, tehtava_id=None, sarja_id=None,talletettu=""):
        """
        Määritää tehtävän.
        Parametrit:
                -kisa_nimi:en lisäksi täytyy määrittää joko tehtävä_id tai sarja_id
                -kun tehtava_id on määritelty, muokataan sen mukaista tehtävää
                -muuten luodaan uutta tehtävää halutulle sarjalle
        """
        posti=None
        if request.method == 'POST':
                posti=request.POST

        tehtava = None
        sarja = None
        if tehtava_id:
                tehtava=get_object_or_404(Tehtava, id=tehtava_id)
                sarja= tehtava.sarja
        
        else:
                sarja = tehtava=get_object_or_404(Sarja, id=sarja_id)
                tehtava=Tehtava(sarja)

        # Tabs:
        tabs= []
        daatta={}
        ot_index=0
        if tehtava_id:
                osatehtavat= tehtava.osatehtava_set.all() 
                for ot in osatehtavat :
                        tabs.append(ot.nimi) 
                        ot_index+=1 
                daatta =luoTehtavaData([tehtava]) 
        # Muutama ylimaarainen tabi:
        for i in range(5) :
                tabs.append( string.letters[ot_index] )
                ot_index+=1
        
        # Haetaan suurin kaytosssa oleva jarjestysnro tassa sarjassa:
        sarjan_tehtavat=Tehtava.objects.filter(sarja=sarja)
        nro =0 
        for t in sarjan_tehtavat :
                if nro < t.jarjestysnro : nro = t.jarjestysnro
        
        # Luodaan tehtavan maaritys form
        maaritaTehtava = tehtavanMaaritysForm(posti,daatta,sarja_id=sarja_id,suurin_jarjestysnro=nro)
        
        # Tallennetaan formin muokkaama data
        tehtava_id=tallennaTehtavaData( daatta ) 
        
        if posti and not 'lisaa_maaritteita' in posti.keys() and daatta['valid'] :
                return HttpResponseRedirect("/tupa/"+kisa_nimi+"/maarita/tehtava/"+str(tehtava_id)+'/talletettu/' )
        else:
                tal=""
                if talletettu=="talletettu" and not posti : tal="Talletettu!"
                
                return render_to_response('tupa/maarita.html', 
                                { 'forms': [maaritaTehtava],
                                'tabs' : tabs ,
                                'heading' : "Valitse tehtävä",
                                'taakse' : "/tupa/"+kisa_nimi+"/maarita/tehtava/" ,
                                'talletettu': tal})

def syotaKisa(request, kisa_nimi,tarkistus=None):
        """
        Valitsee kisan tehtävän jonka tuloksia ruvetaan syöttämään.
        """
        sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
        taulukko = []
        for s in sarjat :
                tehtavat = s.tehtava_set.all()
                for t in tehtavat:
                        t.linkki = "tehtava/"+str(t.id)+"/" 
                        t.nimi = str(t.jarjestysnro)+". " + t.nimi 
                tehtavat.id=s.id
                tehtavat.otsikko=s.nimi
                taulukko.append( tehtavat )
        return render_to_response('tupa/valitse_linkki.html', 
                                { 'taulukko' : taulukko,
                                'heading' : "Valitse tehtävä",
                                'taakse' : "/tupa/"+kisa_nimi+"/" })

def syotaTehtava(request, kisa_nimi , tehtava_id,talletettu=None,tarkistus=None) :
        """
        Määrittää tehtävän syötteet.
        """
        tehtava = get_object_or_404(Tehtava, id=tehtava_id)
        maaritteet = SyoteMaarite.objects.filter(osa_tehtava__tehtava=tehtava)
        vartiot = Vartio.objects.filter(sarja = tehtava.sarja )
        syoteFormit = []
        posti=None
        if request.method == 'POST':
                posti=request.POST
                if 'tarkistettu' in posti.keys():  tehtava.tarkistettu=True
                else : tehtava.tarkistettu=False
        tarkistettu=tehtava.tarkistettu
        validi=True
        for v in vartiot :
                rivi=[]
                for m in maaritteet :
                        syotteet = Syote.objects.filter(vartio = v ).filter(maarite=m)
                        syote=None
                        formi=None
                        if syotteet:
                                syote=syotteet[0]
                        if tarkistus : formi =  TarkistusSyoteForm(m,v,posti,instance=syote,prefix=v.nimi+str(m.pk),)
                        else : formi = SyoteForm(m,v,posti,instance=syote,prefix=v.nimi+str(m.pk),)
                        if syote and syote.arvo and syote.tarkistus :
                                if not syote.arvo==syote.tarkistus :
                                        try: 
                                                if not Decimal(syote.arvo)==Decimal(syote.tarkistus):
                                                        formi.syottovirhe="virhe"
                                        except : formi.syottovirhe="virhe"
                        if formi.is_valid() :
                                formi.save()
                        else :
                                validi=False
                        rivi.append( formi )
                syoteFormit.append( (v,rivi))
        
        if posti and validi  :
                tehtava.save()
                if tarkistus : 
                        osoite="/tupa/"+kisa_nimi+"/syota/tarkistus/tehtava/"+str(tehtava.id)+'/talletettu/'
                        return HttpResponseRedirect( osoite )
                else : return HttpResponseRedirect("/tupa/"+kisa_nimi+"/syota/tehtava/"+str(tehtava.id)+'/talletettu/' )
        else:
                tal=""
                if talletettu=="talletettu" and not posti : tal="Talletettu!"
                tilanne=tehtavanTilanne(tehtava)
                return render_to_response('tupa/syota_tehtava.html', 
                        { 'tehtava' : tehtava ,
                        'maaritteet' : maaritteet ,
                        'syotteet' : syoteFormit,
                        'talletettu': tal ,
                        'tilanne' : tilanne,
                        'tarkistettu' : tarkistettu,
                        'tarkistus' : tarkistus} )

def testiTulos(request, kisa_nimi,talletettu=None):
        """
        Määrittää kisalle testitulokset. Eli ns "oikeat" tulokset, 
        joita voidaan testeissä verrata laskennan tuottamiin tuloksiin.
        """
        taulukko=[]
        sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
        taulukko = []
        posti=None
        if request.method == 'POST':
                posti=request.POST
        
        validi=True
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
                                else :
                                        validi=False
                                v.formit.append( formi )
                taulut.otsikko=s.nimi
                taulut.id=s.id
                taulukko.append(taulut)
        if posti and validi:
                return HttpResponseRedirect("/tupa/"+kisa_nimi+"/maarita/testitulos/talletettu/")
        tal=""
        if talletettu=="talletettu" and not posti : tal="Talletettu!"

        return render_to_response('tupa/testitulos.html',
                        { 'taulukko' : taulukko ,
                        'heading' : "Testittuloksien määritys" ,
                        'taakse' : "/tupa/"+kisa_nimi+"/",
                        'talletettu': tal })

def tuomarineuvos(request, kisa_nimi,talletettu=None):
        """
        Määrittää kisalle testitulokset. Eli ns "oikeat" tulokset, 
        joita voidaan testeissä verrata laskennan tuottamiin tuloksiin.
        """
        taulukko=[]
        sarjat = Sarja.objects.filter(kisa__nimi=kisa_nimi)
        taulukko = []
        posti=None
        if request.method == 'POST':
                posti=request.POST
        
        validi=True
        for s in sarjat :
                taulut=s
                taulut.tiedot=Vartio.objects.filter(sarja=s)
                tehtavat=Tehtava.objects.filter(sarja = s )

                for v in taulut.tiedot:
                        v.tehtavat=tehtavat
                        v.formit=[]
                        for t in tehtavat:
                                formi=TuomarineuvosForm(posti,
                                                v,
                                                t,
                                                prefix=kisa_nimi+s.nimi+t.nimi+v.nimi)
                                if formi.is_valid():
                                        formi.save()
                                else :
                                        validi=False
                                v.formit.append( formi )
                taulut.otsikko=s.nimi
                taulut.id=s.id
                taulukko.append(taulut)
        if posti and validi:
                return HttpResponseRedirect("/tupa/"+kisa_nimi+"/maarita/tuomarineuvos/talletettu/")
        tal=""
        if talletettu=="talletettu" and not posti : tal="Talletettu!"

        return render_to_response('tupa/testitulos.html',
                        { 'taulukko' : taulukko ,
                        'heading' : "Tuomarineuvoksen antamien tulosten määritys" ,
                        'taakse' : "/tupa/"+kisa_nimi+"/",
                        'talletettu': tal })

def tulostaSarja(request, kisa_nimi, sarja_id) :
        """
        Sarjan tulokset.
        """
        sarja = Sarja.objects.get(id=sarja_id)
        tulokset= sarja.laskeTulokset()
        return render_to_response('tupa/tulokset.html', {'tulos_taulukko' : tulokset }  )

def piirit(request,kisa_nimi) :
        """
        Piirikohtaiset tulokset.
        """
        return HttpResponse(kisa_nimi + " PIIRIN TULOSTUS" )

def kopioiTehtavia(request,kisa_nimi,sarja_id ):
        """
        Valitsee ja kopioi valitut saman kisan tehtävät määriteltyyn sarjaan.
        """
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
                                      'taakse' : "/tupa/"+kisa_nimi+"/maarita/tehtava/",
                                      'napin_tyyppi' : 'kopioi' })


def tallennaKisa(request, kisa_nimi):
        """
        Palauttaa käyttäjälle valitun kisan xml formaatissa.
        Jättää henkilöt ja allergiat tallentamatta.
        """
        kisa = get_object_or_404(Kisa, nimi=kisa_nimi)

        response = HttpResponse( kisa_xml(kisa) , mimetype='application/xml')
        response['Content-Disposition'] = 'attachment; filename=tietokanta.xml'
        return response

class UploadFileForm(forms.Form):
        file  = forms.FileField()

class UploadFileNameForm(forms.Form):
        file  = forms.FileField()
        name = forms.CharField(label = "Tallennetaan nimelle")

def saveNewId(object,changeDict,keyName):
        id=object.id
        object.id=None
        object.save()
        changeDict[keyName][id]=object.id
        return object

def korvaaKisa(request,kisa_nimi=None):
        try :
                kisa=Kisa.objects.get(nimi=kisa_nimi)
        except : 
                kisa=None
        
        otsikko=u"korvaa kisa tiedostosta"
        if not kisa_nimi : otsikko =u"lisää kisa tiedostosta "

        form = None
        if request.method == 'POST':
                if not kisa_nimi : form = UploadFileNameForm(request.POST, request.FILES)
                else : form = UploadFileForm(request.POST, request.FILES)
                
                if form.is_valid():
                        if not kisa_nimi : 
                                kisa_nimi = form.cleaned_data['name']
                                try :
                                        kisa=Kisa.objects.get(nimi=kisa_nimi)
                                except : 
                                        kisa=None
                        
                        xml=r""
                        for chunk in request.FILES['file'].chunks():
                                xml+=chunk

                        kisat=[]
                        sarjat=[]
                        vartiot=[]
                        tehtavat=[]
                        testaustulokset=[]
                        tuomarit=[]
                        osatehtavat=[]
                        maaritteet=[]
                        syotteet=[]
                        parametrit=[]

                        for obj in serializers.deserialize("xml", xml):
                                if type(obj.object)==Kisa : kisat.append(obj.object)
                                elif type(obj.object)==Sarja: sarjat.append(obj.object)
                                elif type(obj.object)==Vartio : vartiot.append(obj.object)
                                elif type(obj.object)==Tehtava : tehtavat.append(obj.object)
                                elif type(obj.object)==TestausTulos : testaustulokset.append(obj.object)
                                elif type(obj.object)==TuomarineuvosTulos : tuomarit.append(obj.object)
                                elif type(obj.object)==OsaTehtava : osatehtavat.append(obj.object)
                                elif type(obj.object)==SyoteMaarite : maaritteet.append(obj.object)
                                elif type(obj.object)==Syote : syotteet.append(obj.object)
                                elif type(obj.object)==Parametri : parametrit.append(obj.object)
                        
                        translations={'kisat':{},
                                        'sarjat':{},
                                        'vartiot':{},
                                        'tehtavat':{},
                                        'testaustulokset':{},
                                        'tuomarit':{},
                                        'osatehtavat':{},
                                        'maaritteet': {} ,
                                        'syotteet': {},
                                        'parametrit' : {} }
                        
                        if not len(kisat)==1 : return HttpResponseRedirect('/tupa/'+kisa_nimi+'/korvaa/')
                        elif kisa : kisa.delete()
                        kisat[0].nimi=kisa_nimi
                        saveNewId(kisat[0],translations,"kisat")
                        for s in sarjat:
                                s.kisa_id = translations["kisat"][s.kisa_id]
                                saveNewId(s,translations,"sarjat")
                        for v in vartiot:
                                v.sarja_id = translations["sarjat"][v.sarja_id]
                                saveNewId(v,translations,"vartiot")
                        for t in tehtavat:
                                t.sarja_id = translations["sarjat"][t.sarja_id]
                                saveNewId(t,translations,"tehtavat")
                        for t in testaustulokset:
                                t.tehtava_id = translations["tehtavat"][t.tehtava_id]
                                t.vartio_id = translations["vartiot"][t.vartio_id]
                                saveNewId(t,translations,"testaustulokset")
                        for t in tuomarit:
                                t.tehtava_id = translations["tehtavat"][t.tehtava_id]
                                t.vartio_id = translations["vartiot"][t.vartio_id]
                                saveNewId(t,translations,"tuomarit")
                        for o in osatehtavat:
                                o.tehtava_id = translations["tehtavat"][o.tehtava_id]
                                saveNewId(o,translations,"osatehtavat")
                        for m in maaritteet:
                                m.osa_tehtava_id = translations["osatehtavat"][m.osa_tehtava_id]
                                saveNewId(m,translations,"maaritteet")
                        for s in syotteet:
                                s.maarite_id = translations["maaritteet"][s.maarite_id]
                                s.vartio_id = translations["vartiot"][s.vartio_id]
                                saveNewId(s,translations,"syotteet")
                        for p in parametrit:
                                p.osa_tehtava_id = translations["osatehtavat"][p.osa_tehtava_id]
                                saveNewId(p,translations,"parametrit")

                        return HttpResponseRedirect('/tupa/'+kisa_nimi+'/')
        else:
                if not kisa_nimi : 
                        form = UploadFileNameForm()
                else :form = UploadFileForm()


        return render_to_response('tupa/upload.html', { 'heading' : otsikko , 
                                                        'form' : form , })


def post_txt(request,parametrit):
        """
        Apunäkymä virhetilanteisiin. (error 500,server internal error)
        -Luo kisan tietokannan xml formaattiin ja lisää perään post_data:n testausta varten.
        -Palauttaa xml tiedoston.
        """
        from xml.dom.minidom import  parseString
        kisa_nimi = re.search(r'^osoite=/tupa/(\w+)/',parametrit).group(1)
        kisa = get_object_or_404(Kisa, nimi=kisa_nimi)
        test_data=kisa_xml(kisa)  
        post_data= parametrit.split("&")
        doc = parseString( test_data )
        post_test = doc.createElement('post_request')
        post_test.setAttribute("address", post_data[0].split('=')[1])

        for p in post_data[1:]:
                data=p.split('=')
                elem = doc.createElement('input')
                elem.setAttribute("name", data[0] )
                elem.setAttribute("value", data[1] )
                post_test.appendChild(elem)
        doc.childNodes[0].appendChild(post_test) 
        
        response = HttpResponse(doc.toprettyxml(indent="  "), mimetype='application/xml')
        response['Content-Disposition'] = 'attachment; filename=tietokanta.xml'
        return response

def raportti_500(request) :
        """
        Html Error 500 sivu (Server internal error), 
        Suomeksi: kipa vaan todennäköisesti kaatui.
        -Sisältää linkin joka palauttaa tietokannan,
        sekä viimeisimmän post datan xml formaatissa testausta varten.
        """
        linkki=SafeUnicode('<a href=/tupa/post_txt/'+'osoite='+request.path )
        if len(request.raw_post_data):
                linkki+='&'+request.raw_post_data
        linkki+='/> #00000000'+ str(random.uniform(1, 10)) +'</a>'      
        return render_to_response('500.html', {'error': SafeUnicode(linkki) })

#def tulostaSarjaPDF(request,kisa_nimi,sarja_id):
	"""
	Sarjan tulokset PDF:ksi. Tämän laskennan voisi varmaan toteuttaa jossain muualla, mut kokeilin nyt vain /Joonas
	"""
	"""sarja = Sarja.objects.get(id=sarja_id)
	tulokset= sarja.laskeTulokset()
	# return render_to_response('tupa/tulokset.html', {'tulos_taulukko' : tulokset }  )


	# Create the HttpResponse object with the appropriate PDF headers.
	response = HttpResponse(mimetype='application/pdf')
	response['Content-Disposition'] = 'attachment; filename='+kisa_nimi+sarja_id

	from reportlab.lib.pagesizes import A4, landscape, portrait
	width, height = A4 #keep for later

	# Create the PDF object, using the response object as its "file."
	c = canvas.Canvas(response, pagesize=landscape(A4))

	# Draw things on the PDF. Here's where the PDF generation happens.
	# See the ReportLab documentation for the full list of functionality.
	c.drawString(100, 100, "Hello world.")
"""
	'''from reportlab.lib.units import inch
	# move the origin up and to the left
	c.translate(inch,inch)
	# define a large font
	c.setFont("Helvetica", 14)
	# choose some colors
	c.setStrokeColorRGB(0.2,0.5,0.3)
	c.setFillColorRGB(1,0,1)
	# draw some lines
	c.line(0,0,0,1.7*inch)
	c.line(0,0,1*inch,0)
	# draw a rectangle
	c.rect(0.2*inch,0.2*inch,1*inch,1.5*inch, fill=1)
	# make text go straight up
	c.rotate(90)
	# change color
	c.setFillColorRGB(0,0,0.77)
	# say hello (note after rotate the y coord needs to be negative!)
	c.drawString(0.3*inch, -inch, "Hello World")'''
"""
	from reportlab.lib.units import inch
	from reportlab.lib.colors import magenta, red
	c.setFont("Times-Roman", 20)
	c.setFillColor(red)
	c.drawCentredString(2.75*inch, 2.5*inch, "Font size examples")
	c.setFillColor(magenta)
	size = 7

	# PDF:n otsikko
	c.setTitle('Tulokset')

	# Close the PDF object cleanly, and we're done.
	c.showPage()
	c.save()
	return response
"""
def tulostaSarjaHTML(request, kisa_nimi, sarja_id) :
        """
        Sarjan tulokset, sivu muotoiltuna tulostusta varten, ilman turhia grafiikoita.
        """
        sarja = Sarja.objects.get(id=sarja_id)
        tulokset= sarja.laskeTulokset()
        return render_to_response('tupa/tuloksetHTML.html', {'tulos_taulukko' : tulokset }  )

def luoTestiTulokset(request,kisa_nimi,sarja_id):
        """
        Luo testitulokset valitulle sarjalle ja tallentaa ne kantaan
        """
        def haeTulos(sarjanTulokset, vartio, tehtava) :
                """
                Hakee Vartion pisteet tehtävälle määritellystä tulostaulukosta
                """
                for vart_nro in range(1,len(sarjanTulokset)-1) :
                        for teht_nro in range(2,len(sarjanTulokset[vart_nro])):
                                tulokset =sarjanTulokset[vart_nro][teht_nro]
                                if sarjanTulokset[vart_nro][0] ==vartio and sarjanTulokset[0][teht_nro] ==tehtava:
                                        return tulokset
        
        sarja = get_object_or_404(Sarja , id=sarja_id )
        tulokset= sarja.laskeTulokset()
        for t in sarja.tehtava_set.all() :
                for v in sarja.vartio_set.all() :
                        tulos = haeTulos( tulokset, v , t)
                        tt , p = TestausTulos.objects.get_or_create(vartio=v,tehtava=t )
                        tt.pisteet=str(tulos)
                        tt.save()
        return HttpResponseRedirect("/tupa/"+kisa_nimi+"/maarita/testitulos/" )

def laskennanTilanne(request,kisa_nimi) :
        kisa= get_object_or_404(Kisa , nimi=kisa_nimi )
        taulukko=[[]]
        taulukko[0].append("Tehtava")
        
        suurin = 0
        # Otsikkorivi
        for s in kisa.sarja_set.all() :
                taulukko[0].append(s.nimi)
                for t in s.tehtava_set.all() : 
                        if t.jarjestysnro > suurin: suurin =t.jarjestysnro
        
        # Luodaan taulukko
        for i in range(suurin) :
                rivi= [i+1]
                for s in kisa.sarja_set.all() :
                        rivi.append("")
                taulukko.append(rivi)
        rivi=['valmiina']
        for s in kisa.sarja_set.all() :
                rivi.append("")

        taulukko.append(rivi)
        sarake=1
        for s in kisa.sarja_set.all() :
                vartioita=len(s.vartio_set.all())
                for t in s.tehtava_set.all() :
                        taulukko[t.jarjestysnro][sarake]= tehtavanTilanne(t)
                syotteita=len( Syote.objects.filter(maarite__osa_tehtava__tehtava__sarja=s) )
                maaritteita=len( SyoteMaarite.objects.filter(osa_tehtava__tehtava__sarja=s) )
                if syotteita>0 : 
                        prosentit=Decimal(syotteita*100)/(maaritteita*vartioita)
                        prosentit=prosentit.quantize(Decimal('1.'), rounding=ROUND_UP)
                        taulukko[suurin+1][sarake]= str(prosentit)+"%"
                else: taulukko[suurin+1][sarake]= "0%"
                sarake+=1
                        
        return render_to_response('tupa/laskennan_tilanne.html', {'taulukko' : taulukko,
                                                        "taakse" :"/tupa/"+kisa_nimi+"/" }  )

