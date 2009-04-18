# coding: latin-1
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import modelformset_factory
from django.forms.util import ValidationError
from django import forms
from TulosLaskin import *
from models import *
from django.forms import ModelForm

class TehtavaForm(ModelForm):
    class Meta:
          model = Tehtava
          fields = ('nimi', 'jarjestysnro','kaava')


class PisteSyoteForm(ModelForm):
    class Meta:
          model = Syote

def luoKaavaFormit(tehtavalle=None,post=None,tyhjia=0):
    KaavaFormSet = modelformset_factory( OsapisteKaava,extra=tyhjia,can_delete=True,exclude=('tehtava',))
    return KaavaFormSet(post,queryset=OsapisteKaava.objects.filter(tehtava=tehtavalle) )

def luoMaariteFormit(tehtavalle=None,post=None,tyhjia=0):
    MaariteFormSet = modelformset_factory( SyoteMaarite,extra=tyhjia,can_delete=True,exclude=('tehtava',))
    return MaariteFormSet(post,queryset=SyoteMaarite.objects.filter(tehtava=tehtavalle) )

def luoVartioFormit(sarjalle,post=None,tyhjia=0):
    VartioFormSet = modelformset_factory( Vartio,fields=('nro', 'nimi'),extra=tyhjia,can_delete=True)
    return VartioFormSet(post,queryset=Vartio.objects.filter(sarja=sarjalle),prefix=sarjalle.nimi )
    
class KisaForm(ModelForm):
     class Meta:
        model = Kisa

def luoSarjaFormit(kisalle,post=None,tyhjia=0):
    SarjaFormSet = modelformset_factory( Sarja,exclude=('kisa',),extra=tyhjia,can_delete=True )
    formit=SarjaFormSet(post, queryset=Sarja.objects.filter(kisa=kisalle) )
    return formit

class AikaSyoteForm(forms.Form) :
       h = forms.IntegerField(required=False,widget=forms.TextInput(attrs={'size':'1'}))
       min = forms.IntegerField(required=False,widget=forms.TextInput(attrs={'size':'1'}))
       s = forms.IntegerField(required=False,widget=forms.TextInput(attrs={'size':'1'}))

       def __init__(self,maarite,vartio,post=None) : 
           """
           Pakolliset parametrit ovat:
               -Syötteen määrite jota formi edustaa
               -Vartio jota formi edustaa
           Optionaaliset:
               -Sivun post data jossa kentään syödetyt tiedot.
           """
           self.maarite=maarite
           syotteet = Syote.objects.filter(vartio = vartio ).filter(maarite=maarite)
           self.syote=None
           if syotteet:
               self.syote=syotteet[0]
           self.vartio=vartio
           prefix = "aika_syote_" + str(self.maarite.id) + "_" + str(self.vartio.id)
           initial ={}
           if self.syote and self.syote.arvo:
                  tunnit=divmod(Decimal(self.syote.arvo) , 60*60)[0]
                  minuutit=divmod(Decimal(self.syote.arvo) , 60)[0]- tunnit*60
                  sekuntit= Decimal(self.syote.arvo) - tunnit*60*60 -minuutit*60
                  h = tunnit
                  min = minuutit
                  s = sekuntit
                  initial= { "h" : h, "min" : min , "s" : s }    
           super(forms.Form, self).__init__(post,prefix=prefix,initial=initial)

       def save(self) :
           if self.is_valid() :
               tunnit= self.cleaned_data["h"]
               minuutit= self.cleaned_data["min"]
               sekuntit= self.cleaned_data["s"]
               
               if not tunnit==None or not minuutit==None or not sekuntit==None :
                  arvo=Decimal(0)
                  if tunnit :
                      arvo=arvo + tunnit*60*60
                  if minuutit:
                      arvo=arvo + minuutit*60
                  if sekuntit:
                      arvo= arvo + sekuntit

                  if not self.syote:
                      self.syote=Syote()
                      self.syote.maarite=self.maarite
                      self.syote.vartio=self.vartio
                  self.syote.arvo = str(arvo)
                  self.syote.save()
               else:
                  if self.syote:
                      self.syote.delete()
                      self.syote = None

