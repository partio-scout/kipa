# coding: latin-1
from django.forms.models import modelformset_factory
from django import forms
from models import *
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from decimal import *
import re

class VartioForm(ModelForm):
        ulkopuolella = forms.IntegerField(widget=forms.TextInput(attrs={'size':'2'} ) ,required=False)
        keskeyttanyt = forms.IntegerField(widget=forms.TextInput(attrs={'size':'2'} ) ,required=False)
        class Meta:
                model = Vartio

class KaavaForm(ModelForm):
        kaava = forms.CharField(widget=forms.Textarea)
        class Meta:
                model = OsapisteKaava

KaavaFormSet = inlineformset_factory(Tehtava,OsapisteKaava,extra=3 ,form=KaavaForm)
MaariteFormSet = inlineformset_factory(Tehtava,SyoteMaarite,extra=3 )
VartioFormSet = inlineformset_factory(Sarja,Vartio,extra=10,fields=('nro','nimi',"ulkopuolella","keskeyttanyt",),form=VartioForm )
SarjaFormSet = inlineformset_factory(Kisa,Sarja,extra=4 )
TehtavaValintaFormSet = inlineformset_factory(Sarja,Tehtava,fields='jarjestysnro')


#TehtavaForm
def tupaform_factory(model,overrides,excludeFields=None,fields=None) :
    class uusi(ModelForm) :
        def __init__(self,post,instance=None,sarja=None) :
        
            super(ModelForm,self).__init__(post,instance=instance)
        def save(self):
            pass
        class Meta:
            pass
    return uusi

class TehtavaForm(ModelForm):
    kaava = forms.CharField(widget=forms.TextInput(attrs={'size':'40'} ) ,required=True)
    
    def __init__(self,post,instance=None,sarja=None) :
        self.sarja=sarja
        super(ModelForm,self).__init__(post,instance=instance)
    def save(self):
        tehtava = super(ModelForm,self).save(commit=False)
        tehtava.sarja=self.sarja
        tehtava.save()
        return tehtava
    class Meta:
        fields =  ('nimi', 'jarjestysnro','kaava')
        model = Tehtava

class PisteSyoteForm(ModelForm):
    arvo = forms.FloatField(required=False,widget=forms.TextInput(attrs={'size':'8'} ) )
    def __init__(self,maarite,vartio,*argv,**argkw) :
          self.arvo=forms.TimeField(required=False)
          super(ModelForm,self).__init__(*argv,**argkw)
          self.maarite=maarite
          self.vartio=vartio
    def save(self):
          syote = super(ModelForm,self).save(commit=False)
          syote.maarite=self.maarite
          syote.vartio=self.vartio
          if not self.cleaned_data['arvo']== None :
              syote.arvo = self.cleaned_data['arvo']
              syote.save()
          elif syote.id :
              syote.delete()
    class Meta:
          exclude = ('maarite','vartio')
          model = Syote

class AikaSyoteForm(PisteSyoteForm) :
       arvo=forms.CharField(required=False,widget=forms.TextInput(attrs={'size':'8'}))
       def clean_arvo(self):
           arvo=self.cleaned_data['arvo']
           haku = re.match(r"^(\d*):(\d*):(\d*)\Z",arvo)    
           if haku:
              return str(int(haku.group(1))*60*60 + int(haku.group(2))*60 + int(haku.group(3)))
           elif not arvo :
              return arvo
           else :
              raise forms.ValidationError('Syota aikaa muodossa: (hh:mm:ss)')

def SyoteForm(*argv,**argkw) :
    if argv[0].tyyppi=="aika":
       syotteet=Syote.objects.filter(maarite=argv[0]).filter(vartio=argv[1])
       aikaVakio= None
       if syotteet and syotteet[0].arvo :
           arvo = Decimal(syotteet[0].arvo)
           h = divmod(arvo , 60*60)[0]
           min = divmod(arvo , 60)[0]- h*60
           sec = arvo - (h*60*60) - (min*60)
           aikaVakio = str(h) +":"+str(min) +":"+str(sec)
       return AikaSyoteForm(initial={ 'arvo': aikaVakio },*argv,**argkw)
    else :
       return PisteSyoteForm(*argv,**argkw)

class TestiTulosForm(ModelForm):
        pisteet=pisteet = forms.CharField(required=False)

        def __init__(self,posti,vartio,tehtava,*argv,**argkw) :
                objektit=TestausTulos.objects.filter(vartio=vartio,tehtava=tehtava)
                self.vartio=vartio
                self.tehtava=tehtava
                if len(objektit):
                        super(ModelForm,self).__init__(posti,instance=objektit[0],*argv,**argkw)
                else :
                        super(ModelForm,self).__init__(posti,*argv,**argkw)
        def save(self):
                tulos = super(ModelForm,self).save(commit=False)
                tulos.vartio=self.vartio
                tulos.tehtava=self.tehtava
                if tulos.pisteet == None :
                                if tulos.id :
                                        tulos.delete()
                elif len(tulos.pisteet)==0 :
                                if tulos.id :
                                        tulos.delete()
                else :
                        tulos.save()
                return tulos
        class Meta:
                fields=("pisteet")
                model = TestausTulos

class KisaForm(ModelForm):
     class Meta:
        model = Kisa

class PoistaTehtavaForm(ModelForm):
        class Meta:
                model = Tehtava


