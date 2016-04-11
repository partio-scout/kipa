# !/usr/bin/env python
# -*- coding: utf-8 -*-
# KiPa(KisaPalvelu), tuloslaskentajarjestelma partiotaitokilpailuihin
#    Copyright (C) 2016  Espoon Partiotuki ry. ept@partio.fi
"""
Formit
"""
from django import forms
from django.forms import ModelForm, modelformset_factory
from django.forms import inlineformset_factory as inline_factory
import re

from . import models

############
#  Formit  #
############


class KisaForm(ModelForm):
    class Meta:
        model = models.Kisa
        fields = ["nimi", "aika", "paikka", "tunnistus"]
        labels = {
            "nimi": "Nimi:",
            "aika": "Aika",
            "paikka": "Paikka",
            "tunnistus": "Tunnistus"
        }


class SarjaForm(ModelForm):
    class Meta:
        model = models.Sarja
        fields = ["nimi", "teht1", "teht2", "teht3"]
        labels = {
            "nimi": "Nimi:",
            "teht1": "Tasapisteissä määräävät tehtävät: 1:",
            "teht2": "2:",
            "teht3": "3"
        }


class VartioForm(ModelForm):
    class Meta:
        model = models.Vartio
        fields = ['keskeyttanyt', 'ulkopuolella', 'nro']

VartioFormSet = inline_factory(models.Sarja,
                               models.Vartio,
                               extra=30,
                               fields=('nro', 'nimi', 'lippukunta', 'piiri',
                                       "ulkopuolella", "keskeyttanyt",),
                               form=VartioForm)

MaariteFormSet = inline_factory(models.OsaTehtava, models.SyoteMaarite,
                                fields='__all__',
                                extra=3)

TehtavaValintaFormSet = inline_factory(models.Sarja,
                                       models.Tehtava,
                                       fields=('jarjestysnro',))

class TuhoaTehtavaForm(ModelForm):
    # nimi = forms.CharField(widget=forms.HiddenInput,
                           # required=False)
    # tehtavaryhma = forms.CharField(widget=forms.HiddenInput,
                                   # required=False)
    # tehtavaluokka = forms.CharField(widget=forms.HiddenInput,
                                    # required=False)
    # rastikasky = forms.CharField(widget=forms.HiddenInput, required=False)
    # jarjestysnro = forms.CharField(widget=forms.HiddenInput,
                                   # required=False)
    # kaava = forms.CharField(widget=forms.HiddenInput, required=False)
    # sarja = forms.ModelChoiceField(queryset=models.Sarja.objects.all(),
                                   # widget=forms.HiddenInput,required=False)
    # tarkistettu = forms.BooleanField(widget=forms.HiddenInput,
                                     # required=False)
    # lyhenne = forms.CharField(widget=forms.HiddenInput, required=False)
    # maksimipisteet = forms.CharField(widget=forms.HiddenInput,
                                     # required=False)
    # svirhe = forms.BooleanField(widget=forms.HiddenInput, required=False)
    class Meta:
        model = models.Tehtava
        fields = ['nimi', 'tehtavaryhma', 'tehtavaluokka', 'rastikasky',
                  'jarjestysnro', 'kaava', 'sarja', 'tarkistettu', 'lyhenne',
                  'maksimipisteet', 'svirhe']




tuhoaTehtaviaFormset = modelformset_factory(models.Tehtava,
                                            can_delete=True,
                                            extra=0,
                                            form=TuhoaTehtavaForm)


class TehtavaLinkkiListaFormset(tuhoaTehtaviaFormset):
    def __unicode__(self):
        piirto=unicode(self.management_form)
        for form in self.forms:
            linkki=""
            nimi=""
            if form.instance:
                linkki = unicode(form.instance.id)+"/"
                nimi = unicode(form.instance.jarjestysnro) + ". "
                nimi += unicode(form.instance.nimi)
            piirto += "<a href="+linkki+">" + nimi + "</a>  "
            piirto += form.as_p() + "<br>"
            piirto = piirto.replace("<p>","").replace("</p>","")
        return piirto


class HelpWidget(forms.TextInput):
        """
        Help widget for help text labels
        """
        def __init__(self, helptext, *argcv):
            super(HelpWidget, self).__init__(*argcv)
            self.helptext=helptext

        def render(self, name, value=None, attrs=None):
            return (SafeUnicode(super(HelpWidget, self)
                                .render(name, value, attrs)) +
                    '<span onmouseover="tooltip.show(\''+ self.helptext +'\'' +
                    ')  ;" onmouseout="tooltip.hide();"><img src="/kipamedia' +
                    '/help_small.png" /></span>')


class AikaWidget(forms.TextInput):
    """
    Text input widget, exept for value formatting field values are
    converted from total seconds to "hh:mm:ss"
    """
    def render(self, name, value,attrs=None):
        newValue=value
        if newValue:
            try:
                float(newValue)
                arvo = Decimal(newValue)
                h = int(divmod(arvo, 60*60)[0])
                min = int(divmod(arvo, 60)[0]- h*60)
                sec = int(arvo - (h*60*60) - (min*60))
                if h < 10:
                    h = "0" + str(h)
                if min < 10:
                    min = "0" + str(min)
                if sec < 10:
                    sec = "0" + str(sec)
                newValue = str(h) + ":" + str(min) + ":" + str(sec)
            except ValueError:
                pass
        return super(AikaWidget,self).render(name,newValue,attrs)


class PisteField(forms.CharField):
    """
    Decimal field accepting "kesk",h and,/. as decimal delimiter
    """
    def clean(self, value):
        value = value.strip()
        haku = re.match(r"^((\d*)[,.]?\d+)$",value)
        if haku:
            merkkijono = '0' + haku.group(0)
            return unicode(Decimal(merkkijono.replace(",",".")))
        if value=="kesk":
            return value
        elif value=="h":
            return "h"
        elif value=="H":
            return "h"
        elif value=="e":
            return "e"
        elif value=="E":
            return "e"
        elif value=="":
            return value
        else:
            raise forms.ValidationError('Anna desimaaliluku!')

class AikaField(forms.CharField):
    """
    Validates field input as "hh:mm:ss"
    Converts input to an string number, time in seconds.
    """
    def clean(self, value):
        value = value.strip()
        super(AikaField, self).clean(value)
        haku = re.match(r"^(\d+):(\d+):(\d+)$",value)
        if haku:
            return unicode((int(haku.group(1)) * 60 * 60 +
                            int(haku.group(2)) * 60 + int(haku.group(3))))
        elif not value:
            return None
        elif value=="kesk":
            return value
        elif value=="h":
            return "h"
        elif value=="H":
            return "h"
        elif value=="e":
            return "e"
        elif value=="E":
            return "e"
        else:
            raise forms.ValidationError('Syötä aikaa muodossa: hh:mm:ss')


def initPisteSyote(self, fieldName):
    kesk= self.vartio.keskeyttanyt
    nro = self.maarite.osa_tehtava.tehtava.jarjestysnro
    if not kesk==None and not nro==None:
        if kesk <= nro:# Keskeyttänyt
            self.fields[fieldName].widget.attrs["class"] = "kesk"
            self.fields[fieldName].widget.attrs['readonly'] = True
            self.initial[fieldName] = "kesk"


def savePisteSyote(self, syote, field, fieldName, alternateName):
    syote.maarite=self.maarite
    syote.vartio=self.vartio
    if self.cleaned_data[fieldName] or self.cleaned_data[alternateName]:
        field = self.cleaned_data[fieldName]
        syote.save()
    elif syote.id:
        syote.delete()

class PisteSyoteForm(ModelForm):
    arvo = PisteField(required=False,
                      widget=forms.TextInput(attrs={'size':'16',
                                                    'class':'numeric'}))
    tarkistus = PisteField(required=False,widget=forms.HiddenInput)
    def __init__(self, maarite, vartio, *argv, **argkw):
        super(ModelForm,self).__init__(*argv,**argkw)
        self.maarite=maarite
        self.vartio=vartio
        initPisteSyote(self,"arvo")
    def save(self):
        syote = super(ModelForm,self).save(commit=False)
        savePisteSyote(self,syote,syote.arvo,"arvo","tarkistus")
    class Meta:
        exclude = ('maarite','vartio')
        model = models.Syote

class PisteTarkistusForm(ModelForm):
    tarkistus = PisteField(required=False,
                           widget=forms.TextInput(attrs={'size':'16',
                                                         'class':'numeric'}))
    arvo = PisteField(required=False, widget=forms.HiddenInput)
    def __init__(self, maarite, vartio, *argv, **argkw):
        super(ModelForm, self).__init__(*argv, **argkw)
        self.maarite = maarite
        self.vartio = vartio
        initPisteSyote(self, "tarkistus")
    def save(self):
        syote = super(ModelForm, self).save(commit=False)
        savePisteSyote(self, syote, syote.tarkistus, "tarkistus", "arvo")
    class Meta:
        exclude = ('maarite','vartio')
        model = models.Syote

class AikaSyoteForm(PisteSyoteForm):
    arvo = AikaField(required=False,
                     widget=AikaWidget(attrs={'class': 'time','value': ''}))

class AikaTarkistusForm(PisteTarkistusForm):
    tarkistus = AikaField(required=False,
                          widget=AikaWidget(attrs={'class': 'time',
                                                   'value': ''}))

def SyoteForm(*argv, **argkw):
    if argv[0].tyyppi == "aika":
        return AikaSyoteForm(*argv, **argkw)
    else:
        return PisteSyoteForm(*argv, **argkw)

def TarkistusSyoteForm(*argv, **argkw):
    if argv[0].tyyppi == "aika":
        return AikaTarkistusForm(*argv, **argkw)
    else:
        return PisteTarkistusForm(*argv, **argkw)

###############################################################
############## Tuomarineuvos ja TestiTulos ####################
###############################################################

def tulostauluFormFactory(tauluTyyppi):
    class tulostauluForm:
        def __init__(self, posti, vartio, tehtava, *argv, **argkw):
            self.taulu = None
            self.posti = posti
            self.errors = ""
            self.id = ("tuomarineuvos_" + str(vartio.id) +
                       "_" + str(tehtava.id))
            try:
                self.taulu = tauluTyyppi.objects.get(vartio=vartio,
                                                     tehtava=tehtava)
            except tauluTyyppi.DoesNotExist:
                pass
            self.vartio=vartio
            self.tehtava=tehtava
        def is_valid(self):
            if self.posti and self.id in self.posti.keys():
                self.pisteet = self.posti[self.id]
                return 1
            else:
                return None
        def save(self):
            tulos=None
            if self.pisteet == None or len(self.pisteet)==0  and self.taulu:
                self.taulu.delete()
            if self.pisteet and len(self.pisteet):
                tulos = tauluTyyppi.objects.get_or_create(vartio=self.vartio,
                                                          tehtava=self.tehtava)
                tulos.pisteet=self.pisteet
                tulos.save()
                self.taulu=tulos
            return tulos
        def __unicode__(self):
            formidata = {"name": self.id, "id": self.id, "value": "",
                         "errors": self.errors}
            if self.taulu:
                formidata["value"] = self.taulu.pisteet
            return render_to_string("tupa/forms/tulostaulu.html",
                                    dict(formidata))
    return tulostauluForm

TuomarineuvosForm = tulostauluFormFactory(models.TuomarineuvosTulos)
TestiTulosForm = tulostauluFormFactory(models.TestausTulos)

####################################################################


# class PoistaTehtavaForm(ModelForm):
        # class Meta:
                # model = models.Tehtava

class UploadFileForm(forms.Form):
        file  = forms.FileField()

class UploadFileNameForm(forms.Form):
    file  = forms.FileField()
    name = forms.CharField(label = "Tallennetaan nimelle")
    def clean_name(self):
        nimi = self.cleaned_data['name']
        nimi = re.sub(r'\s', '_',nimi)
        kisat = models.Kisa.objects.all()
        for k in kisat:
            if k.nimi == nimi:
                raise forms.ValidationError("Nimi on jo käytössä")
        return nimi

SarjaFormSet = inline_factory(models.Kisa, models.Sarja,
                              exclude=('kisa',), extra=6)
