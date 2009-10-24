from models import *
from formit import *
from django.forms import ModelForm
from django import forms

from django.utils.safestring import SafeUnicode
from django.template.loader import render_to_string
import re 
import string

class RadioBRWidget(forms.RadioSelect):
        """
        Widget for drawing radiobuttons separated with <br> tags.
        Works with forms being drawn as_ul().
        """
        def render(self, name, *args, **kwargs):
                """
                Renders field with all <li><ul> tags removed and replaced with <br> tags.
                """
                html = super(RadioBRWidget, self).render(name, *args, **kwargs)
                muokattu = html.replace("<li>","")
                muokattu = muokattu.replace("</li>","<br>")
                muokattu = muokattu.replace("<ul>","")
                muokattu = muokattu.replace("</ul>","")
                ilman=muokattu.rpartition("<br>")
                return SafeUnicode(ilman[0]+ilman[2])

class PartRadioWidget(forms.RadioSelect):
        """
        Widget for separating radio buttons with custom positions for single choices.
        (to position radio buttons of the same choice set separately anywhere in the page)
        """
        def __init__(self,choice_name,field_name,*args, **kwargs):
                """
                Takes 2 required parameters
                choice_name = name of the choice that the widget is only going to render.
                field_name = name of the orginal field that this field is based on.
                """
                super(forms.RadioSelect, self).__init__( *args, **kwargs)
                self.choice_name=choice_name
                self.field_name=field_name

        def render(self, name,data ,*args, **kwargs):
                """
                Renders only the radio button specified in self.choice_name.
                Renames the field name as self.field_name.
                """
                id=kwargs['attrs']['id']+"_"+self.field_name
                checked=""
                nimi=name
                if self.field_name:
                        oikea = re.search(r"(.*?"+self.field_name+").*", name )
                        if oikea:
                                nimi= oikea.group(1)
                if self.choice_name==data :
                        checked='checked="checked"'
                html = '<input '+checked+' type="radio" id="'+id+'" value="'+self.choice_name+'" name="'+nimi+'" />'
                return SafeUnicode(html)

class TextBRWidget(forms.TextInput):
        """
        Widget for rendering text input field ending with <br> tag.
        """
        def render(self, name, *args, **kwargs):
                html = super(TextBRWidget, self).render(name, *args, **kwargs)
                muokattu = html.replace("<p>","")
                muokattu = muokattu.replace("</p>","")
                return SafeUnicode(muokattu + "<br>")
class AikaBRWidget(AikaWidget):
        """
        Widget for rendering aika input field ending with <br> tag.
        """
        def render(self, name, *args, **kwargs):
                html = super(AikaBRWidget, self).render(name, *args, **kwargs)
                muokattu = html.replace("<p>","")
                muokattu = muokattu.replace("</p>","")
                return SafeUnicode(muokattu + "<br>")

class PisteMaariteForm(ModelForm):
        kali_vihje=forms.CharField(label="Syotteen kuvaus",widget=TextBRWidget,required=False)
        #minArvo=forms.CharField(label="Sallitut Arvot",required=False)
        #maxArvo=forms.CharField(label=" - ",required=False)
        maarite_tyyppi="piste"
        maarite_nimi="a"
        tyyppi="osatehtavan tyyppi"
        class Meta:
                fields=("kali_vihje","minArvo","maxArvo")
                model=SyoteMaarite

        def __init__(self,posti,osaTehtava,*argv,**argkw ): 
                if osaTehtava.tyyppi==self.tyyppi :
                        try:
                                sm= SyoteMaarite.objects.get(nimi=self.maarite_nimi,osa_tehtava=osaTehtava)
                                super(PisteMaariteForm,self).__init__(posti ,instance=sm,*argv,**argkw)
                        except SyoteMaarite.DoesNotExist :
                                super(PisteMaariteForm,self).__init__(posti,*argv,**argkw)
                else:
                        super(PisteMaariteForm,self).__init__(posti,*argv,**argkw)
                self.osaTehtava=osaTehtava

        def save(self):

                sm=None
                try:
                        sm= SyoteMaarite.objects.get(nimi=self.maarite_nimi,osa_tehtava=self.osaTehtava)
                except SyoteMaarite.DoesNotExist :
                        sm=None

                maarite=super(ModelForm,self).save(commit=False)
                if sm : maarite.pk = sm.pk
                maarite.nimi = self.maarite_nimi
                maarite.tyyppi = self.maarite_tyyppi
                maarite.osa_tehtava = self.osaTehtava
                maarite.save()
                return maarite

        def __unicode__(self):
                return SafeUnicode(render_to_string("tupa/forms/syote_maarite.html", 
                                                        {'form': self ,}))

class KisaPisteForm(PisteMaariteForm):
        tyyppi="kp"
        label="Kisapisteita"       
                
class RaakaPisteForm(PisteMaariteForm):
        tyyppi="rp"
        label="Raakapisteita"   

class AikaForm(PisteMaariteForm) : 
        tyyppi="ka"
        #minArvo=forms.CharField(widget=forms.HiddenInput(),required=False)
        #maxArvo=forms.CharField(widget=forms.HiddenInput(),required=False)
        maarite_tyyppi="aika"
        label="Kokonaisaika"  

class AlkuaikaForm(AikaForm) :
        tyyppi="ala"
        kali_vihje=forms.CharField(label="Syotteen 1 kuvaus: (esim. alkuaika)",widget=TextBRWidget,required=False)

class LoppuaikaForm(AikaForm) :
        tyyppi="ala"
        maarite_nimi="b"
        kali_vihje=forms.CharField(label="Syotteen 2 kuvaus: (esim. loppuaika)",widget=TextBRWidget,required=False)

class AlkuLoppuAika(forms.Form):
        tyyppi="ala"
        label="Alkuaika ja loppuaika"
        def __init__(self,posti,osaTehtava,*argv,**argkw ):
                super(forms.Form,self).__init__(*argv,**argkw)
                prefixi=""
                if argkw['prefix']: prefixi = argkw['prefix']
                argkw['prefix']='alkuaika_'+prefixi
                self.alkuaika=AlkuaikaForm(posti,osaTehtava,*argv,**argkw )
                argkw['prefix']="loppuaika_"+prefixi
                self.loppuaika=LoppuaikaForm(posti,osaTehtava,*argv,**argkw )
                self.osaTehtava=osaTehtava
        def save(self):
                if self.tyyppi==self.osaTehtava.tyyppi:
                        self.alkuaika.save()
                        self.loppuaika.save()
        def is_valid(self):
                return self.alkuaika.is_valid() and self.loppuaika.is_valid()
        def __unicode__(self):
                return self.alkuaika.__unicode__()+self.loppuaika.__unicode__()


MaariteFormset = inlineformset_factory(OsaTehtava,SyoteMaarite,fields=("nimi","kali_vihje","tyyppi"),extra=3 )

class VapaaKaava(MaariteFormset):
        tyyppi="vk"
        label="Alkuaika ja loppuaika"

        kaava = forms.CharField(required = False)
        def __init__(self,posti,osaTehtava,*argv,**argkw ):
                super(MaariteFormset,self).__init__(posti,instance=osaTehtava,*argv,**argkw)
                self.osaTehtava=osaTehtava
        def __unicode__(self,*args, **kwargs):
                return SafeUnicode(render_to_string("tupa/forms/vapaa_kaava.html", 
                                                        {'form': self,
                                                        "maariteFormset" : self }))
        label="Vapaa kaava"

class MaksimiSuoritus(forms.Form):
        parhaatChoices= (("p","pienin:"),("s","suurin:"),("k","kiintea:"))
        parhaat=  forms.ChoiceField(choices=parhaatChoices,widget=forms.RadioSelect,required=False)
        kiintea= forms.FloatField(label="",widget=TextBRWidget,required=False)
        jaettavat = forms.FloatField(required=False )
        label="Maksimisuoritus"
        def __init__(self,posti,osaTehtava,*argv,**argkw ):
                assert osaTehtava
                self.maxP = Parametri.objects.get_or_create(nimi="maxP",osa_tehtava=osaTehtava )[0]
                self.aMax = Parametri.objects.get_or_create(nimi="aMax",osa_tehtava=osaTehtava )[0]
                jaettavat= self.maxP.arvo
                parhaat= self.aMax.arvo 
                kiintea_a=None
                pienin = re.match( r"^pienin\((.*)\)$"   , parhaat ) 
                suurin = re.match( r"^suurin\((.*)\)$"   , parhaat ) 
                if pienin :
                        parhaat="p"
                elif suurin:
                        parhaat="s"
                else :
                        kiintea_a=parhaat
                        parhaat="k"
                initial= { }
                if re.match(".*?"+osaTehtava.tyyppi+".*?",argkw['prefix']) :
                        initial= {'parhaat' : parhaat , 'kiintea' : kiintea_a , 'jaettavat' : jaettavat }
                super(MaksimiSuoritus,self).__init__(posti,initial=initial,*argv,**argkw)
                self.osaTehtava=osaTehtava
        
        def clean_kiintea(self):
                cd= self.cleaned_data
                if "parhaat" in cd.keys() and cd["parhaat"]=="k" :
                        if not "kiintea" in cd.keys() or not cd["kiintea"] :
                                raise forms.ValidationError("Syota kiitea arvo tai valise suurin/pienin!")
                return cd["kiintea"]
        def clean_parhaat(self):
                cd= self.cleaned_data
                if not "parhaat" in cd.keys() or not cd["parhaat"] :
                                raise forms.ValidationError("Valitse kiitea arvo suurin/pienin!")
                return cd["parhaat"]


        def save(self) :
                self.maxP.arvo=self.cleaned_data['jaettavat']
                parhaat= self.cleaned_data['parhaat']
                if parhaat=="k":
                        self.aMax.arvo= self.cleaned_data['kiintea']
                elif parhaat=="p" :
                        self.aMax.arvo= "pienin(maksimi_kaava)"
                else:
                        self.aMax.arvo= "suurin(maksimi_kaava)"

                self.maxP.save()
                self.aMax.save()

        def __unicode__(self,*args, **kwargs):
                return SafeUnicode(render_to_string("tupa/forms/maksimi_suoritus.html", {'form': self}))
        class Meta:
                fields= ("parhaat","kiintea","jaettavat")
                model= OsaTehtava

class MaksimiAika(MaksimiSuoritus):
        kiintea= AikaField(label="",widget=AikaBRWidget,required=False)


class NollaSuoritus(forms.Form):
        kerroinChoices=(("1.5","1.5 (pienin tulos saa parhaat pisteet)"),
                        ("0.5","0.5 (suurin tulos saa parhaat pisteet)"),
                        ("m","muu"))
        valintaChoices=(("ki","kiintea"),("ke","kerroin"))
        valinta= forms.ChoiceField(initial="" ,choices=valintaChoices,widget=forms.RadioSelect,required=False)
        valinta_ki= forms.ChoiceField(widget=PartRadioWidget("ki","valinta"),
                                choices=OsaTehtava.OSA_TYYPIT,label="",required=False)
        valinta_ke= forms.ChoiceField(widget=PartRadioWidget("ke","valinta"),
                                choices=OsaTehtava.OSA_TYYPIT,label="",required=False)

        kiintea= forms.FloatField(label="kiintea suoritus",widget=TextBRWidget,required=False)
        kerroin= forms.ChoiceField(choices=kerroinChoices,widget=RadioBRWidget,required=False)
        muu= forms.FloatField(label="muu",required=False)
        label="NollaSuoritus"
        def __init__(self,posti,osaTehtava,*argv,**argkw ):
                assert osaTehtava
                self.osaTehtava=osaTehtava
                self.nolla=None
                try:
                        self.nolla = Parametri.objects.get(nimi="nolla",osa_tehtava=osaTehtava )
                except Parametri.DoesNotExist:
                        pass
                
                self.nollaKerroin = Parametri.objects.get_or_create(nimi="nolla_kerroin",osa_tehtava=osaTehtava )[0]
                aKiintea= None
                aKerroin= None
                aMuu = None
                aValinta = None
                
                nolla_arvo=None
                if self.nolla : nolla_arvo=self.nolla.arvo
                rKerroin = re.match( r"med\((.*)\)$"   ,str( nolla_arvo) ) 
                if rKerroin :
                        if self.nollaKerroin.arvo=="1.5" or self.nollaKerroin.arvo=="0.5":
                                aKerroin = self.nollaKerroin.arvo
                        else :
                                aKerroin = "m"
                                aMuu = self.nollaKerroin.arvo
                        aValinta = "ke"
                else :
                        aValinta = "ki"
                        aKiintea= nolla_arvo

                super(NollaSuoritus,self).__init__(posti,*argv,**argkw)
                
                pInit=None
                aInitial= self.initial.copy()
                if not posti and re.match(".*?"+osaTehtava.tyyppi+".*?",argkw['prefix']) :
                        aInitial['kiintea']= aKiintea
                        aInitial['kerroin']= aKerroin
                        aInitial['muu'] = aMuu 
                        aInitial['valinta'] = aValinta 
                        aInitial['valinta_ki'] = aValinta 
                        aInitial['valinta_ke'] = aValinta 
                if posti:   
                        pInit=posti.copy()
                        prefix=argkw['prefix']
                        if prefix+'-valinta' in pInit.keys():
                                arvo= pInit[prefix+'-valinta']
                                #print "arvo " + arvo
                                #print prefix+"-valinta"
                                pInit[prefix+'-valinta'] =arvo#pInit[prefix+'-valinta']
                                pInit[prefix+'-valinta_ki'] =arvo#pInit[prefix+'-valinta']
                                pInit[prefix+'-valinta_ke'] =arvo#pInit[prefix+'-valinta']
                super(NollaSuoritus,self).__init__(pInit,*argv,**argkw)
        def clean_valinta(self):
                cd = self.cleaned_data
                #print cd
                #if not "valinta" in cd.keys() or not cd["valinta"]:
                        #print "aaaa" 
                        #print "valinta " +str(cd["valinta"])
                        #raise forms.ValidationError("Valitse kiitea arvo tai kerroin")
                return cd["valinta"]
        def clean_kiintea(self):
                cleaned_data = self.cleaned_data
                if  "valinta" in cleaned_data.keys() and cleaned_data["valinta"]=="ki" :
                        if not "kiintea" in  cleaned_data.keys() or not cleaned_data["kiintea"]  :
                                raise forms.ValidationError("Syota kiitea arvo tai valise kerroin")
                return cleaned_data["kiintea"]
        def clean_kerroin(self):
                cleaned_data = self.cleaned_data
                if  "valinta" in cleaned_data.keys() and cleaned_data["valinta"]=="ke" :
                        if not "kerroin" in cleaned_data.keys() or cleaned_data["kerroin"]=="": 
                                print "ccc"
                                raise forms.ValidationError("Valitse kerroin")
                return cleaned_data["kerroin"]
        def clean_muu(self):
                cleaned_data = self.cleaned_data
                if  "valinta" in cleaned_data.keys() and cleaned_data["valinta"]=="ke" :
                        if "kerroin" in  cleaned_data.keys() and cleaned_data["kerroin"]=="m" :
                                if not "muu" in cleaned_data.keys() or not cleaned_data["muu"]:
                                        raise forms.ValidationError("Syota kerroin")
                return cleaned_data["muu"]

        def save(self) :
                if not self.nolla: self.nolla=Parametri()
                self.nolla.osa_tehtava=self.osaTehtava
                self.nolla.nimi="nolla"

                if self.cleaned_data['valinta']=="ki":
                        self.nolla.arvo= self.cleaned_data['kiintea']
                        self.nollaKerroin.arvo="1"
                else :
                        self.nolla.arvo="med(nolla_kaava)"
                        nKerroin = self.cleaned_data["kerroin"]
                        if nKerroin=="m":
                                self.nollaKerroin.arvo=self.cleaned_data['muu']
                        else :
                                self.nollaKerroin.arvo=nKerroin
                self.nolla.save()
                self.nollaKerroin.save()

        def __unicode__(self,*args,**kwargs):
                return render_to_string("tupa/forms/nolla_suoritus.html", {'form': self})

class NollaAika(NollaSuoritus):
        kiintea= AikaField(label="kiintea suoritus",widget=AikaWidget,required=False)

class Arviointi(forms.Form):
        help_text="""Jos kyseessa on tavallinen tehtava, tata ei valita. Mikali kyseessa on arivointitehtava, tulee tassa ilmoittaa tehtavan oikea vastaus. Talloin vartioiden suoritukset taman arvon molemmin puolin ovat samanarvoisia."""        
        kaytossa=forms.BooleanField(required=False)
        oikea=forms.CharField(label="Oikea vastaus",help_text=help_text,required=False)
        label="Arviointi"
        def __unicode__(self):
                
                return self.as_p()

class test(list) :
        id = None
        otsikko = "testi"

class OsaTehtavaForm(ModelForm) :
        tyyppi= forms.ChoiceField(widget=PartRadioWidget("kp","tyyppi"),
                                choices=OsaTehtava.OSA_TYYPIT,label="",required=False)
        tyyppi_rp= forms.ChoiceField(widget=PartRadioWidget("rp","tyyppi"),
                                choices=OsaTehtava.OSA_TYYPIT,label="",required=False)
        tyyppi_ka= forms.ChoiceField(widget=PartRadioWidget("ka","tyyppi"),
                                choices=OsaTehtava.OSA_TYYPIT,label="",required=False)
        tyyppi_ala= forms.ChoiceField(widget=PartRadioWidget("ala","tyyppi"),
                                choices=OsaTehtava.OSA_TYYPIT,label="",required=False)
        tyyppi_vk= forms.ChoiceField(widget=PartRadioWidget("vk","tyyppi"),
                                choices=OsaTehtava.OSA_TYYPIT,label="",required=False)

        def __init__(self,posti,*args,**kwargs) :
                init = None
                initial={}
                prefix=kwargs['prefix']
                if posti:   
                        init=posti.copy()
                        tyyppi_name= prefix +'-tyyppi' 
                        if tyyppi_name in posti.keys():
                                tyyppi_i = posti[tyyppi_name]
                                init[tyyppi_name]= tyyppi_i
                                init[prefix +'-tyyppi_rp'] = tyyppi_i
                                init[prefix +'-tyyppi_ka'] = tyyppi_i
                                init[prefix +'-tyyppi_ala'] = tyyppi_i
                                init[prefix +'-tyyppi_vk'] = tyyppi_i
                
                super(OsaTehtavaForm, self).__init__(*args, **kwargs)
                tyyppi_i=self.instance.tyyppi
                initial['tyyppi']= tyyppi_i
                initial['tyyppi_rp'] = tyyppi_i
                initial['tyyppi_ka'] = tyyppi_i
                initial['tyyppi_ala'] = tyyppi_i
                initial['tyyppi_vk'] = tyyppi_i

                super(OsaTehtavaForm, self).__init__(init,initial=initial,*args, **kwargs)
                self.taulukko=[]
                self.prefixID=""
                # Parametri formien lisaaminen:
                if self.instance :
                        self.prefixID=str(self.instance.pk)
                        
                        
                        def lisaaMaxNolla(parametrit,prefixID):
                                """
                                # Funktio joka nopeuttaa samankaltaisten maksimi,nolla,arviointi 
                                -parametrien lisaamista
                                """
                                parametrit[-1].append( MaksimiSuoritus( posti,self.instance, 
                                                prefix="maksimi_suoritus_"+prefixID ) )
                                parametrit[-1].append( NollaSuoritus( posti,self.instance,
                                                prefix="nolla_suoritus_"+prefixID ) )
                                #parametrit[-1].append( Arviointi( posti,self.instance,
                                #                prefix="arviointi_"+prefixID ) )
                        # KisaPiste
                        prefixID="kp_"+self.prefixID
                        self.parametrit=test()
                        self.parametrit.append( test([KisaPisteForm( posti,self.instance ,prefix=prefixID )]) )
                        self.parametrit[-1].id=prefixID
                        self.parametrit[-1].otsikko="Kisapiste"
                        # RaakaPiste
                        prefixID="rp_"+self.prefixID
                        self.parametrit.append( test([RaakaPisteForm( posti,self.instance ,prefix=prefixID),]) )
                        lisaaMaxNolla( self.parametrit,prefixID )
                        self.parametrit[-1].id=prefixID
                        self.parametrit[-1].otsikko="Raakapiste"
                        # KokonaisAika
                        prefixID="ka_"+self.prefixID
                        self.parametrit.append( test([AikaForm( posti,self.instance ,prefix=prefixID),]) )
                        #lisaaMaxNolla( self.parametrit,prefixID )
                        self.parametrit[-1].append( MaksimiAika( posti,self.instance, 
                                                prefix="maksimi_suoritus_"+prefixID ) )
                        self.parametrit[-1].append( NollaAika( posti,self.instance,
                                                prefix="nolla_suoritus_"+prefixID ) )
                        #self.parametrit[-1].append( Arviointi( posti,self.instance,
                        #                        prefix="arviointi_"+prefixID ) )

                        self.parametrit[-1].id=prefixID
                        self.parametrit[-1].otsikko="Kokonaisaika"
                        # Alku ja loppuaika
                        prefixID="ala_"+self.prefixID
                        self.parametrit.append( test([AlkuLoppuAika( posti,self.instance ,prefix=prefixID),]) )
                        self.parametrit[-1].append( MaksimiAika( posti,self.instance, 
                                                prefix="maksimi_suoritus_"+prefixID ) )
                        self.parametrit[-1].append( NollaAika( posti,self.instance,
                                                prefix="nolla_suoritus_"+prefixID ) )
                        self.parametrit[-1].id=prefixID
                        self.parametrit[-1].otsikko="Alkuaika ja loppuaika"
                        # Vapaa Kaava

                        #prefixID="vk_"+self.prefixID
                        #self.parametrit.append( test([VapaaKaava( posti,self.instance ,prefix=prefixID),]) )
                        #lisaaMaxNolla( self.parametrit, prefixID )
                        #self.parametrit[-1].id=prefixID
                        #self.parametrit[-1].otsikko="Vapaa Kaava"
                       
        def clean(self):
                cleaned_data = self.cleaned_data
                if not 'tyyppi' in cleaned_data.keys() or cleaned_data['tyyppi']=="" :
                        raise forms.ValidationError("Muista ruksata osatehtavan tyyppi")
                
                tyyppi=self.cleaned_data['tyyppi']
                for param in self.parametrit:
                        for p in param:
                                # Talletetaan ainoastaan sellainen formi joita kaytetaan tassa tyypissa.
                                t= tyyppi+"_" + str(self.instance.id)
                                if re.match(".*?"+ t+".*?",p.prefix) and not p.is_valid():
                                        print p.prefix
                                        print t
                                        print re.match(".*?"+ t+".*?",p.prefix)
                                        print param.otsikko
                                        print "PERKELE!!!"
                                        raise forms.ValidationError("Syota kaikki pakolliset kohdat!")
                return cleaned_data


        def save(self):
                osatehtava=super(OsaTehtavaForm,self).save(commit=False)
                for param in self.parametrit:
                        for p in param:
                                # Talletetaan ainoastaan sellainen formi joita kaytetaan tassa tyypissa.
                                t= osatehtava.tyyppi+"_" + str(self.instance.id)
                                if re.match(".*?"+t+".*?",p.prefix) :
                                        p.save()
                # Eroitellaan sellaiset osatehtavatyypit joiden kaava eroaa vakiosta.
                if osatehtava.tyyppi=="kp":
                        # Kisapisteita, suora summa
                        osatehtava.kaava="ss"
                else :
                        # Yleiskaava suurimmalle osalle osa tehtavista :
                        maksimiKaava = Parametri.objects.get_or_create(nimi="maksimi_kaava",
                                                osa_tehtava=osatehtava)[0]
                        maksimiKaava.arvo="a"
                        nollaKaava = Parametri.objects.get_or_create(nimi="nolla_kaava",
                                                osa_tehtava=osatehtava)[0]
                        nollaKaava.arvo="a"
                        osatehtava.kaava="interpoloi(a,aMax,maxP,nolla_kerroin*nolla)"

                        if osatehtava.tyyppi=="ala":

                                # Alku ja loppu aika (loppuaika-alkuaika)
                                maksimiKaava.arvo="b-a"
                                nollaKaava.arvo="b-a"
                                osatehtava.kaava="interpoloi(b-a,aMax,maxP,nolla_kerroin*nolla)"
                
                        maksimiKaava.save()
                        nollaKaava.save()
                
                if not osatehtava.tyyppi=="ala" and not osatehtava.tyyppi=="vk" :
                        p_maaritteet= SyoteMaarite.objects.filter(osa_tehtava=osatehtava).exclude(nimi="a")
                        p_maaritteet.delete()

                osatehtava.save()
        def __unicode__(self) :
                tab_id = "ot_tab_id_" + self.prefixID
                return render_to_string("tupa/forms/osa_tehtava.html", 
                                        { 'form': self,
                                        'tab_id' : tab_id ,
                                        'taulukko' : self.parametrit})
        class Meta :
                fields=("tyyppi")
                model = OsaTehtava

class TehtavaForm(ModelForm):
        kaava = forms.CharField(initial="ss",widget=forms.TextInput(attrs={'size':'40'} ) ,required=True)
        osatehtavia = forms.IntegerField(required=False)
        def __init__(self,posti,instance=None,sarja=None) :
                self.sarja=sarja
                osatehtavia=1 
                self.posti=posti
                if instance :
                        osatehtavia=len(OsaTehtava.objects.filter(tehtava=instance) )
                self.osaTehtavaFormit= []
                for ot in OsaTehtava.objects.filter(tehtava=instance):
                        self.osaTehtavaFormit.append(OsaTehtavaForm(posti,
                                                                instance=ot,
                                                                prefix="osatehtava_"+str(ot.pk)))

                super(ModelForm,self).__init__(posti,instance=instance,initial={'osatehtavia': osatehtavia })
        def clean(self):
                cleaned_data = self.cleaned_data
                for ot in self.osaTehtavaFormit :
                        if not ot.is_valid():
                                raise forms.ValidationError("Tarkista maaritys!")
                return cleaned_data

        def save(self):
                tehtava = super(ModelForm,self).save(commit=False)
                tehtava.sarja=self.sarja
                tehtava.save()
                osa_tehtavat= OsaTehtava.objects.filter(tehtava=tehtava)
        
                osatehtavia=self.cleaned_data['osatehtavia']
                for ot in self.osaTehtavaFormit :
                        ot.save()

                valmiit_osatehtavat = 0
                if osa_tehtavat :
                        valmiit_osatehtavat=len(osa_tehtavat)
                # luodaan uusia osatehtavia:
                if osatehtavia > valmiit_osatehtavat :
                        for ot in range( (osatehtavia-valmiit_osatehtavat ) ) :
                                uusiOT = OsaTehtava()
                                uusiOT.nimi=string.letters[ot+valmiit_osatehtavat]
                                uusiOT.tehtava=tehtava
                                uusiOT.save()
                # poistetaan vanhoja osatehtavia:
                elif valmiit_osatehtavat > osatehtavia :
                        poistettavat=[]
                        for ot in range( osatehtavia , valmiit_osatehtavat ) :
                                if osa_tehtavat[ot].id :
                                        osa_tehtavat[ot].delete()
                else:   pass
                return tehtava
        def __unicode__(self) :
                return render_to_string("tupa/forms/tehtava.html", 
                                                        {'form': self, 
                                                'osa_tehtavat' : self.osaTehtavaFormit})
        class Meta:
                fields =  ('nimi', 'jarjestysnro','kaava')
                model = Tehtava

