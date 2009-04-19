# coding: latin-1
from django.forms.models import modelformset_factory
from django import forms
from models import *
from django.forms import ModelForm
from django.forms.models import inlineformset_factory

KaavaFormSet = inlineformset_factory(Tehtava,OsapisteKaava,extra=3 )
MaariteFormSet = inlineformset_factory(Tehtava,SyoteMaarite,extra=3 )
VartioFormSet = inlineformset_factory(Sarja,Vartio,extra=10,fields=('nro','nimi') )
SarjaFormSet = inlineformset_factory(Kisa,Sarja,extra=4 )


class TehtavaForm(ModelForm):
    def __init__(self,post,instance=None,sarja=None) :
        self.sarja=sarja
        super(ModelForm,self).__init__(post,instance=instance)
    def save(self):
        tehtava = super(ModelForm,self).save(commit=False)
        tehtava.sarja=self.sarja
        tehtava.save()
        return tehtava
    class Meta:
        model = Tehtava
        fields = ('nimi', 'jarjestysnro','kaava')

class PisteSyoteForm(ModelForm):
    arvo = forms.FloatField(required=False)
    def __init__(self,maarite=None,vartio=None,*argv,**argkw) :
          super(ModelForm,self).__init__(*argv,**argkw)
          self.maarite=maarite
          self.vartio=vartio
    def save(self):
          syote = super(ModelForm,self).save(commit=False)
          syote.maarite=self.maarite
          syote.vartio=self.vartio
          if self.cleaned_data['arvo'] :
              syote.save()
          elif syote.id :
              syote.delete()
    class Meta:
          exclude = ('maarite','vartio')
          model = Syote

class KisaForm(ModelForm):
     class Meta:
        model = Kisa

