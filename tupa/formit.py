# coding: latin-1
from django.forms.models import modelformset_factory
from django import forms
from models import *
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from decimal import *
import re
from django.utils.safestring import SafeUnicode

class VartioForm(ModelForm):
        ulkopuolella = forms.IntegerField(
                        widget=forms.TextInput(attrs={'size':'2'} ) ,
                        required=False)
        keskeyttanyt = forms.IntegerField(widget=forms.TextInput(attrs={'size':'2'} ) ,required=False)
        class Meta:
                model = Vartio

VartioFormSet = inlineformset_factory(Sarja,
                                Vartio,
                                extra=30,
                                fields=('nro','nimi','lippukunta','piiri',"ulkopuolella", "keskeyttanyt",),
                                form=VartioForm )

MaariteFormSet = inlineformset_factory(OsaTehtava,SyoteMaarite,extra=3 )
SarjaFormSet = inlineformset_factory(Kisa,Sarja,extra=8 )
TehtavaValintaFormSet = inlineformset_factory(Sarja,Tehtava,fields='jarjestysnro')

tuhoaTehtaviaFormset = modelformset_factory(Tehtava,can_delete=True,extra=0,fields=('delete'))
class TehtavaLinkkilistaFormset(tuhoaTehtaviaFormset):
        def __unicode__(self) :
                piirto=unicode(self.management_form)
                for form in self.forms :
                        linkki=""
                        nimi=""
                        if form.instance:
                                linkki=str(form.instance.id)+"/"
                                nimi=str(form.instance.jarjestysnro)+". "+str(form.instance.nimi)
                        piirto=piirto+"<a href="+linkki+">"+nimi+"</a>  "+form.as_p()+"<br>" 
                        piirto = piirto.replace("<p>","").replace("</p>","")
                return SafeUnicode(piirto)



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

class PisteField(forms.FloatField) :
        """
        Floatfield accepting "kesk",h
        """
        def clean(self, value) :
                if value=="kesk":
                        return value
                elif value=="h":
                        return value
                elif value=="H":
                        return "h"
                else:
                        return super(PisteField, self).clean(value)

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
                elif value=="kesk":
                        return value
                elif value=="h":
                        return "h"
                elif value=="H":
                        return "h"
                else :
                        raise forms.ValidationError('Syota aikaa muodossa: (hh:mm:ss)')

class PisteSyoteForm(ModelForm):
        arvo = PisteField(required=False,widget=forms.TextInput(attrs={'size':'8'} ) )
        
        def __init__(self,maarite,vartio,*argv,**argkw) :
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
                if self.cleaned_data['arvo'] == "kesk":
                        pass
                elif not self.cleaned_data['arvo']== None :
                        syote.arvo = self.cleaned_data['arvo']
                        syote.save()
                elif syote.id :
                        syote.delete()
        class Meta:
                exclude = ('maarite','vartio')
                model = Syote

class AikaSyoteForm(PisteSyoteForm) :
        arvo=AikaField(required=False,widget=AikaWidget( attrs={'class': 'TCMask[##:##:##]','value': ''} ))
           
def SyoteForm(*argv,**argkw) :
        if argv[0].tyyppi=="aika":
                return AikaSyoteForm(*argv,**argkw)
        else :
                return PisteSyoteForm(*argv,**argkw)

class TestiTulosForm(ModelForm):
        pisteet = forms.CharField(required=False,widget=forms.TextInput(attrs={'size':'4'} ))

        def __init__(self,posti,vartio,tehtava,*argv,**argkw) :
                objekti=None
                try : objekti=TestausTulos.objects.get(vartio=vartio,tehtava=tehtava)
                except TestausTulos.DoesNotExist : pass
                self.vartio=vartio
                self.tehtava=tehtava
                if objekti:
                        super(ModelForm,self).__init__(posti,instance=objekti,*argv,**argkw)
                else :
                        super(ModelForm,self).__init__(posti,*argv,**argkw)
        def save(self):
                tulos = super(ModelForm,self).save(commit=False)
                tulos.vartio=self.vartio
                tulos.tehtava=self.tehtava
                if tulos.pisteet == None or len(tulos.pisteet)==0  and tulos.id  : 
                        tulos.delete()
                else : tulos.save()
                return tulos
        class Meta:
                fields=("pisteet")
                model = TestausTulos

class TuomarineuvosForm(ModelForm):
        pisteet = forms.CharField(required=False,widget=forms.TextInput(attrs={'size':'4'} ))

        def __init__(self,posti,vartio,tehtava,*argv,**argkw) :
                objekti=None
                try : objekti=TuomarineuvosTulos.objects.get(vartio=vartio,tehtava=tehtava)
                except TuomarineuvosTulos.DoesNotExist : pass
                self.vartio=vartio
                self.tehtava=tehtava
                if objekti:
                        super(ModelForm,self).__init__(posti,instance=objekti,*argv,**argkw)
                else :
                        super(ModelForm,self).__init__(posti,*argv,**argkw)
        def save(self):
                tulos = super(ModelForm,self).save(commit=False)
                tulos.vartio=self.vartio
                tulos.tehtava=self.tehtava
                if tulos.pisteet == None or len(tulos.pisteet)==0  and tulos.id  : 
                        tulos.delete()
                else : tulos.save()
                return tulos
        class Meta:
                fields=("pisteet")
                model = TuomarineuvosTulos

class KisaForm(ModelForm):
        class Meta:
                model = Kisa

class PoistaTehtavaForm(ModelForm):
        class Meta:
                model = Tehtava


