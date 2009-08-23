from models import *
from django.forms import ModelForm
from django import forms
from django.forms.models import inlineformset_factory

from django.utils.safestring import SafeUnicode
from django.template.loader import render_to_string
import re 
import string
class RadioBRWidget(forms.RadioSelect):
        def render(self, name, *args, **kwargs):
                html = super(RadioBRWidget, self).render(name, *args, **kwargs)
                muokattu = html.replace("<li>","")
                muokattu = muokattu.replace("</li>","<br>")
                muokattu = muokattu.replace("<ul>","")
                muokattu = muokattu.replace("</ul>","")
                ilman=muokattu.rpartition("<br>")
                return SafeUnicode(ilman[0]+ilman[2])


class TextBR(forms.TextInput):
        def render(self, name, *args, **kwargs):
                html = super(TextBR, self).render(name, *args, **kwargs)
                muokattu = html.replace("<li>","")
                muokattu = muokattu.replace("</li>","")
                return SafeUnicode(muokattu + "<br>")

class OsaTehtavaParametri(forms.Form):
        label="parametri"
        def __init__(self,posti,osaTehtava,*argv,**argkw ):
                super(forms.Form,self).__init__(posti,*argv,**argkw)
                self.osaTehtava=osaTehtava
        class Meta:
                model=Parametri


class KisaPiste(ModelForm):
        def __init__(self,posti,osaTehtava,*argv,**argkw ):
                sm= SyoteMaarite.objects.filter(nimi="kp")
                if len(sm)==1 : 
                        super(KisaPiste,self).__init__(posti,instance=sm[0],*argv,**argkw)
                else:
                        super(KisaPiste,self).__init__(posti,*argv,**argkw)
                self.osaTehtava=osaTehtava
        kali_vihje=forms.CharField(label="Syotteen kuvaus",widget=TextBR)
        minArvo=forms.CharField(label="Sallitut Arvot",required=False)
        maxArvo=forms.CharField(label=" - ",required=False)
        label="Kisapisteita"
        def save(self,commit=True):
                maarite=super(KisaPiste,self).save(commit=False)
                maarite.nimi = "a"
                maarite.tyyppi = "piste"
                maarite.osa_tehtava = self.osaTehtava
                return maarite.save(commit)
        class Meta:
                fields=("kali_vihje","minArvo","maxArvo")
                model=SyoteMaarite

class RaakaPiste(ModelForm):
        kali_vihje=forms.CharField(label="Syotteen kuvaus",widget=TextBR)
        minArvo=forms.CharField(label="Sallitut Arvot",required=False)
        maxArvo=forms.CharField(label=" - ",required=False)
        label="Raakapisteita"
        def __init__(self,posti,osaTehtava,*argv,**argkw ):
                sm= SyoteMaarite.objects.get_or_create(nimi="a",osa_tehtava=osaTehtava )[0]
                super(ModelForm,self).__init__(posti,instance=sm,*argv,**argkw)
                self.osaTehtava=osaTehtava

        def save(self,commit=True):
                maarite = super(ModelForm,self).save(commit=False)
                maarite.nimi="a"
                maarite.tyyppi = "piste"
                maarite.osa_tehtava = self.osaTehtava
                maarite.save()
        class Meta:
                fields=("kali_vihje","minArvo","maxArvo")
                model=SyoteMaarite

class KokonaisAika(RaakaPiste):
        label="Kokonaisaika"
        def save(self,commit=True):
                maarite = super(ModelForm,self).save(commit=False)
                maarite.nimi="a"
                maarite.tyyppi = "aika"
                maarite.osa_tehtava = self.osaTehtava
                maarite.save()


class AlkuLoppuAika(OsaTehtavaParametri):
        alkuaika=forms.CharField(label="Alkuajan kuvaus: (esim. alkuaika)",widget=TextBR)
        loppuaika=forms.CharField(label="Loppuajan kuvaus: (esim. loppuaika)")
        label="Alkuaika ja loppuaika"

class VapaaKaava(OsaTehtavaParametri):
        kaava = forms.CharField()
        def __unicode__(self,*args, **kwargs):
                return SafeUnicode(render_to_string("tupa/forms/vapaa_kaava.html", {'form': self}))
        label="Vapaa kaava"

class MaksimiSuoritus(forms.Form):
        parhaatChoices= (("p","pienin:"),("s","suurin:"),("k","kiitea:"))
        parhaat=  forms.ChoiceField(choices=parhaatChoices,widget=forms.RadioSelect)
        kiintea= forms.CharField(label="",widget=TextBR,required=False)
        jaettavat = forms.CharField( )
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
                initial= {'parhaat' : parhaat , 'kiintea' : kiintea_a , 'jaettavat' : jaettavat }
                super(MaksimiSuoritus,self).__init__(posti,initial=initial,*argv,**argkw)
                self.osaTehtava=osaTehtava
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

class NollaSuoritus(forms.Form):
        kerroinChoices=(("1.5","1.5 (pienin tulos saa parhaat pisteet)"),
                        ("0.5","0.5 (suurin tulos saa parhaat pisteet)"),
                        ("m","muu"))
        valintaChoices=(("ki","kiintea"),("ke","kerroin"))
        valinta= forms.ChoiceField(choices=valintaChoices,widget=forms.RadioSelect)
        kiintea= forms.CharField(label="kiintea suoritus",widget=TextBR,required=False)
        kerroin= forms.ChoiceField(choices=kerroinChoices,widget=RadioBRWidget,required=False)
        muu= forms.CharField(label="muu",required=False)
        label="NollaSuoritus"
        def __init__(self,posti,osaTehtava,*argv,**argkw ):
                assert osaTehtava
                self.nolla = Parametri.objects.get_or_create(nimi="nolla",osa_tehtava=osaTehtava )[0]
                self.nollaKerroin = Parametri.objects.get_or_create(nimi="nolla_kerroin",osa_tehtava=osaTehtava )[0]
                aKiintea= None
                aKerroin= None
                aMuu = None
                aValinta = None

                rKerroin = re.match( r"med\((.*)\)$"   ,str(self.nolla.arvo) ) 
                if rKerroin :
                        if self.nollaKerroin.arvo=="1.5" or self.nollaKerroin.arvo=="0.5":
                                aKerroin = self.nollaKerroin.arvo
                        else :
                                aKerroin = "m"
                                aMuu = self.nollaKerroin.arvo
                        aValinta = "ke"
                else :
                        aValinta = "ki"
                        aKiintea= self.nolla.arvo
                
                aInitial= { 'kiintea' : aKiintea , 'kerroin' : aKerroin, 'muu' : aMuu , 'valinta': aValinta  }
                if posti:
                        super(NollaSuoritus,self).__init__(posti,*argv,**argkw)
                else:
                        super(NollaSuoritus,self).__init__(posti,initial=aInitial,*argv,**argkw)

        def save(self) :
                if self.cleaned_data['valinta']=="ki":
                        self.nolla.arvo= self.cleaned_data["kiintea"]
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

class Arviointi(OsaTehtavaParametri):
        help_text="""Jos kyseessa on tavallinen tehtava, tata ei valita. Mikali kyseessa on arivointitehtava, tulee tassa ilmoittaa tehtavan oikea vastaus. Talloin vartioiden suoritukset taman arvon molemmin puolin ovat samanarvoisia."""        
        kaytossa=forms.BooleanField()
        oikea=forms.CharField(label="Oikea vastaus",help_text=help_text)
        label="Arviointi"


class OsaTehtavaForm(ModelForm) :
        tyyppi= forms.ChoiceField(widget=forms.RadioSelect,choices=OsaTehtava.OSA_TYYPIT,label="",required=False)
        def __init__(self,posti,*args,**kwargs) :
                super(OsaTehtavaForm, self).__init__(posti,*args, **kwargs)
                self.parametrit=[]
                if self.instance :
                        prefixID=str(self.instance.pk)
                        if self.instance.tyyppi=="kp" :
                                self.parametrit.append( KisaPiste( posti,self.instance ,prefix="kp_"+prefixID ) )
                        elif self.instance.tyyppi=="rp" :
                                self.parametrit.append( RaakaPiste( posti,self.instance ,prefix="rp"+prefixID) )
                        elif self.instance.tyyppi=="ka":
                                self.parametrit.append( KokonaisAika( posti,self.instance ,prefix="ka_"+prefixID) )
                        elif self.instance.tyyppi=="ala":
                                self.parametrit.append( AlkuLoppuAika( posti,self.instance ,prefix="ala_"+prefixID) )
                        elif self.instance.tyyppi=="vk":
                                self.parametrit.append( VapaaKaava( posti,self.instance ,prefix="vk_"+prefixID) )
                        if self.instance.tyyppi and not self.instance.tyyppi=="kp":
                                self.parametrit.append( MaksimiSuoritus( posti,self.instance, prefix="maksimi_suoritus_"+prefixID ) )
                                self.parametrit.append( NollaSuoritus( posti,self.instance,prefix="nolla_suoritus_"+prefixID ) )
                                self.parametrit.append( Arviointi( posti,self.instance ) )

        def __unicode__(self) :
                return render_to_string("tupa/forms/osa_tehtava.html", { 'form': self,'parametrit' : self.parametrit })
        def save(self):
                osatehtava=super(OsaTehtavaForm,self).save(commit=False)
                for p in self.parametrit:
                        if p.is_valid() :
                                p.save()
                if osatehtava.tyyppi=="kp":
                        osatehtava.kaava="ss"
                if osatehtava.tyyppi=="ala":
                        maksimiKaava = Parametri.objects.get_or_create(nimi="maksimi_kaava",osa_tehtava=osatehtava)[0]
                        maksimiKaava.arvo="a-b"
                        maksimiKaava.save()
                        nollaKaava = Parametri.objects.get_or_create(nimi="nolla_kaava",osa_tehtava=osatehtava)[0]
                        nollaKaava.arvo="a-b"
                        nollaKaava.save()
                        osatehtava.kaava="interpoloi(a-b,aMax,maxP,nolla_kerroin*nolla)"

                else :
                        
                        maksimiKaava = Parametri.objects.get_or_create(nimi="maksimi_kaava",osa_tehtava=osatehtava)[0]
                        maksimiKaava.arvo="a"
                        maksimiKaava.save()
                        nollaKaava = Parametri.objects.get_or_create(nimi="nolla_kaava",osa_tehtava=osatehtava)[0]
                        nollaKaava.arvo="a"
                        nollaKaava.save()
                        osatehtava.kaava="interpoloi(a,aMax,maxP,nolla_kerroin*nolla)"
                osatehtava.save()

        class Meta :
                fields=("tyyppi")
                model = OsaTehtava


class TehtavaForm(ModelForm):
    kaava = forms.CharField(widget=forms.TextInput(attrs={'size':'40'} ) ,required=True)
    osatehtavia = forms.IntegerField(required=False)
    def __init__(self,posti,instance=None,sarja=None) :
        self.sarja=sarja
        osatehtavia=1 
        if instance :
                osatehtavia=len(OsaTehtava.objects.filter(tehtava=instance) )
        self.osaTehtavat= []
        for ot in OsaTehtava.objects.filter(tehtava=instance):
                self.osaTehtavat.append(OsaTehtavaForm(posti,instance=ot,prefix="osatehtava_"+str(ot.pk)))

        super(ModelForm,self).__init__(posti,instance=instance,initial={'osatehtavia': osatehtavia })
    def save(self):
        tehtava = super(ModelForm,self).save(commit=False)
        tehtava.sarja=self.sarja
        tehtava.save()
        osa_tehtavat= OsaTehtava.objects.filter(tehtava=tehtava)
        
        osatehtavia=self.cleaned_data['osatehtavia']
        for ot in self.osaTehtavat :
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
        else:
                pass
        return tehtava
    def __unicode__(self) :
                return render_to_string("tupa/forms/tehtava.html", {'form': self, 'osa_tehtavat' : self.osaTehtavat})
    class Meta:
        fields =  ('nimi', 'jarjestysnro','kaava')
        model = Tehtava

