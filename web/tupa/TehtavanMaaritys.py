from models import *
from django.forms import ModelForm
from django import forms
from django.forms.models import inlineformset_factory

from django.utils.safestring import SafeUnicode
from django.template.loader import render_to_string

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


class KisaPiste(OsaTehtavaParametri):
        kuvaus=forms.CharField(label="Syotteen kuvaus",widget=TextBR)
        minArvo=forms.CharField(label="Sallitut Arvot")
        maxArvo=forms.CharField(label=" - ")
        label="Kisapisteita"

class RaakaPiste(OsaTehtavaParametri):
        kuvaus=forms.CharField(label="Syotteen kuvaus",widget=TextBR)
        minArvo=forms.CharField(label="Sallitut Arvot")
        maxArvo=forms.CharField(label=" - ")
        label="Raakapisteita"
        
class KokonaisAika(OsaTehtavaParametri):
        kuvaus=forms.CharField(label="Syotteen kuvaus",widget=TextBR)
        label="Kokonaisaika"


class AlkuLoppuAika(OsaTehtavaParametri):
        alkuaika=forms.CharField(label="Alkuajan kuvaus: (esim. alkuaika)",widget=TextBR)
        loppuaika=forms.CharField(label="Loppuajan kuvaus: (esim. loppuaika)")
        label="Alkuaika ja loppuaika"

class VapaaKaava(OsaTehtavaParametri):
        kaava = forms.CharField()
        def __unicode__(self,*args, **kwargs):
                return SafeUnicode(render_to_string("tupa/forms/vapaa_kaava.html", {'form': self}))
        label="Vapaa kaava"


class MaksimiSuoritus(OsaTehtavaParametri):
        parhaatChoices= (("p","pienin:"),("s","suurin:"),("k","kiitea:"))
        parhaat= forms.ChoiceField(choices=parhaatChoices,widget=forms.RadioSelect)
        kiintea= forms.CharField(label="",widget=TextBR)
        jaettavat = forms.CharField()
        label="Maksimisuoritus"
        def __unicode__(self,*args, **kwargs):
                return SafeUnicode(render_to_string("tupa/forms/maksimi_suoritus.html", {'form': self}))

class NollaSuoritus(OsaTehtavaParametri):
        kerroinChoices=(("1.5","1.5 (pienin tulos saa parhaat pisteet)"),
                        ("0.5","0.5 (suurin tulos saa parhaat pisteet)"),
                        ("m","muu"))
        valintaChoices=(("ki","kiintea"),("ke","kerroin"))
        valinta= forms.ChoiceField(choices=valintaChoices,widget=forms.RadioSelect)
        kiintea= forms.CharField(label="kiintea suoritus",widget=TextBR)
        kerroin= forms.ChoiceField(choices=kerroinChoices,widget=RadioBRWidget)
        muu= forms.CharField(label="muu")
        label="NollaSuoritus"
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
                        
                        if self.instance.tyyppi=="kp" :
                                self.parametrit.append( KisaPiste( posti,self.instance ) )
                        elif self.instance.tyyppi=="rp" :
                                self.parametrit.append( RaakaPiste( posti,self.instance ) )
                        elif self.instance.tyyppi=="ka":
                                self.parametrit.append( KokonaisAika( posti,self.instance ) )
                        elif self.instance.tyyppi=="ala":
                                self.parametrit.append( AlkuLoppuAika( posti,self.instance ) )
                        elif self.instance.tyyppi=="vk":
                                self.parametrit.append( VapaaKaava( posti,self.instance ) )
                        if self.instance.tyyppi and not self.instance.tyyppi=="kp":
                                self.parametrit.append( MaksimiSuoritus( posti,self.instance ) )
                                self.parametrit.append( NollaSuoritus( posti,self.instance ) )
                                self.parametrit.append( Arviointi( posti,self.instance ) )

        def __unicode__(self) :
                return render_to_string("tupa/forms/osa_tehtava.html", { 'form': self,'parametrit' : self.parametrit })

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
                        uusiOT.nimi="Osatehtava "+str(ot+valmiit_osatehtavat+1)
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

