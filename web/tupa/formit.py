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

VartioFormSet = inlineformset_factory(Sarja,Vartio,extra=10,fields=('nro','nimi',"ulkopuolella","keskeyttanyt",),form=VartioForm )

MaariteFormSet = inlineformset_factory(OsaTehtava,SyoteMaarite,extra=3 )
SarjaFormSet = inlineformset_factory(Kisa,Sarja,extra=4 )
TehtavaValintaFormSet = inlineformset_factory(Sarja,Tehtava,fields='jarjestysnro')



class AikaWidget(forms.TextInput):
        """
        Text input widget, exept for value formatting field values are converted from total seconds to "hh:mm:ss"
        """
        def render(self, name, value,attrs=None):
                newValue=value
                if newValue :
                     try:
                        float(newValue)
                        arvo = Decimal(newValue)
                        h = divmod(arvo , 60*60)[0]
                        min = divmod(arvo , 60)[0]- h*60
                        sec = arvo - (h*60*60) - (min*60)
                        newValue = str(h) +":"+str(min) +":"+str(sec)
                     except ValueError:
                        pass
                return super(AikaWidget,self).render(name,newValue,attrs)

class AikaField(forms.CharField):
        """
        Validates field input as "hh:mm:ss" 
        Converts input to an string number, time in seconds.
        """
        def clean(self, value) :
                super(AikaField, self).clean(value)
                haku = re.match(r"^(\d+):(\d+):(\d+)$",value)    
                if haku:
                        return str(int(haku.group(1))*60*60 + int(haku.group(2))*60 + int(haku.group(3)))
                elif not value :
                        return None
                else :
                        raise forms.ValidationError('Syota aikaa muodossa: (hh:mm:ss)')

class PisteSyoteForm(ModelForm):
    arvo = forms.FloatField(required=False,widget=forms.TextInput(attrs={'size':'8'} ) )
    def __init__(self,maarite,vartio,*argv,**argkw) :
          #self.arvo=forms.TimeField(required=False)
          super(ModelForm,self).__init__(*argv,**argkw)
          self.maarite=maarite
          self.vartio=vartio
          kesk= self.vartio.keskeyttanyt
          nro = self.maarite.osa_tehtava.tehtava.jarjestysnro
          if kesk and nro :
                if kesk <= nro :
                        self.fields['arvo'].widget.attrs['readonly'] = True
                        self.initial['arvo']= "kesk"

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
        arvo=AikaField(required=False,widget=AikaWidget( attrs={'id': 'aika'} ))
           
def SyoteForm(*argv,**argkw) :
        if argv[0].tyyppi=="aika":
                return AikaSyoteForm(*argv,**argkw)
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


