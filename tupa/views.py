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
from django.utils.safestring import SafeUnicode

from duplicate import kopioiTehtava
from duplicate import kisa_xml

import re
from formit import *
from TehtavanMaaritys import *

from reportlab.pdfgen import canvas

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
        return render_to_response('tupa/tulosta.html', {'sarja_list': sarjat })

def maaritaKisa(request, kisa_nimi=None):
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

def maaritaVartiot(request,kisa_nimi):
        """
        Määritää kisan vartiot sarjoittain.
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
                return HttpResponseRedirect("/tupa/"+kisa_nimi+"/maarita/vartiot/")
        else:
                return render_to_response('tupa/valitse_formset.html',
                                        { 'taulukko' : taulukko ,
                                        'heading' : "Määritä vartiot",
                                        'taakse' : "../../" })

def maaritaTehtava(request, kisa_nimi, tehtava_id=None, sarja_id=None):
        """
        Määritää tehtävän.
        Parametrit:
                -kisa_nimi:en lisäksi täytyy määrittää joko tehtävä_id tai sarja_id
                -kun tehtava_id on määritelty, muokataan sen mukaista tehtävää
                -muuten luodaan uutta tehtävää halutulle sarjalle
        """
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
                ot.label="Osatehtava " + ot.instance.nimi.upper()
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
                                'taakse' : "../" })

def syotaTehtava(request, kisa_nimi , tehtava_id) :
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
                return HttpResponseRedirect("/tupa/"+kisa_nimi+"/maarita/testitulos/")
        return render_to_response('tupa/testitulos.html',
                        { 'taulukko' : taulukko ,
                        'heading' : "Testi tuloksien määritys" ,
                        'taakse' : "../../" })

def tuomarineuvos(request, kisa_nimi):
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
                return HttpResponseRedirect("/tupa/"+kisa_nimi+"/maarita/tuomarineuvos/")
        return render_to_response('tupa/testitulos.html',
                        { 'taulukko' : taulukko ,
                        'heading' : "Tuomarineuvos tuloksien määritys" ,
                        'taakse' : "../../" })

def tulostaSarja(request, kisa_nimi, sarja_id) :
        """
        Sarjan tulokset.
        """
        sarja = Sarja.objects.get(id=sarja_id)
        lokkeri.clearLog()
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
                                      'taakse' : "../../../../tehtava/" })


def tallennaKisa(request, kisa_nimi):
        """
        Palauttaa käyttäjälle valitun kisan xml formaatissa.
        Jättää henkilöt ja allergiat tallentamatta.
        """
        kisa = get_object_or_404(Kisa, nimi=kisa_nimi)

        response = HttpResponse( kisa_xml(kisa) , mimetype='application/xml')
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
        linkki+='/> Post data testaukseen </a>'      
        return render_to_response('500.html', {'error': SafeUnicode(linkki) })

def tulostaSarjaPDF(request,kisa_nimi,sarja_id):
	"""
	Sarjan tulokset PDF:ksi. Tämän laskennan voisi varmaan toteuttaa jossain muualla, mut kokeilin nyt vain /Joonas
	"""
	sarja = Sarja.objects.get(id=sarja_id)
	lokkeri.clearLog()
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

def tulostaSarjaHTML(request, kisa_nimi, sarja_id) :
        """
        Sarjan tulokset, sivu muotoiltuna tulostusta varten, ilman turhia grafiikoita.
        """
        sarja = Sarja.objects.get(id=sarja_id)
        lokkeri.clearLog()
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
                        print tulos
                        tt.save()
        return HttpResponseRedirect("/tupa/"+kisa_nimi+"/maarita/testitulos/" )
        

