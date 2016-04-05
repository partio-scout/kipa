# KiPa(KisaPalvelu), tuloslaskentajärjestelmä partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi


#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.forms.models import modelformset_factory
from django import forms
from django.forms import ModelForm

from .models import *

# class TuhoaTehtavaForm(forms.ModelForm):

    # class Meta:
        # model = TuhoaTehtava
        # fields=['nro', 'nimi', 'lippukunta','piiri','ulkopuolella','keskeyttanyt']

# class TehtavalinkkiListaFormSet(forms.ModelForm):

    # class Meta:
        # model = TehtavalinkkiLista
        # fields=['nro', 'nimi', 'lippukunta','piiri','ulkopuolella','keskeyttanyt']

class KisaForm(forms.ModelForm):

    class Meta:
        model = Kisa
        fields=['nimi']

class SarjaForm(forms.ModelForm):

    class Meta:
        model = Sarja
        fields = ['nimi']

class VartioForm(forms.ModelForm):

    class Meta:
        model = Vartio
        fields=['nro', 'nimi', 'lippukunta','piiri','ulkopuolella','keskeyttanyt']
