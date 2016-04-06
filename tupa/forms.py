# KiPa(KisaPalvelu), tuloslaskentajärjestelmä partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi


# !/usr/bin/env python

from django.forms import ModelForm

from .models import *


class KisaForm(ModelForm):

    class Meta:
        model = Kisa
        fields = ['nimi']


class SarjaForm(ModelForm):
    class Meta:
        model = Sarja
        fields = ['nimi']


class VartioForm(ModelForm):

    class Meta:
        model = Vartio
        fields = ['nro', 'nimi', 'lippukunta',
                  'piiri', 'ulkopuolella', 'keskeyttanyt']
