# encoding: utf-8
# KiPa(KisaPalvelu), tuloslaskentajarjestelma partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi


#!/usr/bin/python

from django.db import models

class Kisa(models.Model) :
        #gen_legacy_class Kisa
        id = models.IntegerField(primary_key=True)
        nimi = models.CharField(max_length=255)
        aika = models.CharField(max_length=255, blank=True)
        paikka = models.CharField(max_length=255)
        class Meta:
            db_table = u'tupa_kisa'
        

        #end_legacy_class

class Sarja(models.Model) :
        #gen_legacy_class Sarja
        id = models.IntegerField(primary_key=True)
        nimi = models.CharField(max_length=255)
        vartion_maksimikoko = models.IntegerField(null=True, blank=True)
        vartion_minimikoko = models.IntegerField(null=True, blank=True)
        kisa = models.ForeignKey(Kisa)
        class Meta:
            db_table = u'tupa_sarja'
        

        #end_legacy_class

class Vartio(models.Model) :
        #gen_legacy_class Vartio
        id = models.IntegerField(primary_key=True)
        nro = models.IntegerField()
        nimi = models.CharField(max_length=255)
        sarja = models.ForeignKey(Sarja)
        piiri = models.CharField(max_length=255)
        lippukunta = models.CharField(max_length=255)
        puhelinnro = models.CharField(max_length=255)
        sahkoposti = models.CharField(max_length=255)
        osoite = models.CharField(max_length=255)
        keskeyttanyt = models.IntegerField(null=True, blank=True)
        ulkopuolella = models.IntegerField(null=True, blank=True)
        class Meta:
            db_table = u'tupa_vartio'
        

        #end_legacy_class

class Henkilo(models.Model) :
        #gen_legacy_class Henkilo
        id = models.IntegerField(primary_key=True)
        nimi = models.CharField(max_length=255)
        syntymavuosi = models.IntegerField(null=True, blank=True)
        lippukunta = models.CharField(max_length=255, blank=True)
        jasennumero = models.CharField(max_length=15, blank=True)
        puhelin_nro = models.CharField(max_length=15, blank=True)
        homma = models.CharField(max_length=255, blank=True)
        class Meta:
            db_table = u'tupa_henkilo'
        

        #end_legacy_class

class Tehtava(models.Model) :
        #gen_legacy_class Tehtava
        id = models.IntegerField(primary_key=True)
        nimi = models.CharField(max_length=255)
        tehtavaryhma = models.CharField(max_length=255)
        tehtavaluokka = models.CharField(max_length=255)
        rastikasky = models.TextField()
        jarjestysnro = models.IntegerField()
        kaava = models.CharField(max_length=255)
        sarja = models.ForeignKey(Sarja)
        tarkistettu = models.BooleanField()
        class Meta:
            db_table = u'tupa_tehtava'
        

        #end_legacy_class
        

class Osatehtava(models.Model) :
        #gen_legacy_class Osatehtava
        id = models.IntegerField(primary_key=True)
        nimi = models.CharField(max_length=255)
        tyyppi = models.CharField(max_length=255)
        kaava = models.CharField(max_length=255)
        tehtava = models.ForeignKey(Tehtava)
        class Meta:
            db_table = u'tupa_osatehtava'
        

        #end_legacy_class

class Syotemaarite(models.Model) :
        #gen_legacy_class Syotemaarite
        id = models.IntegerField(primary_key=True)
        nimi = models.CharField(max_length=255)
        tyyppi = models.CharField(max_length=255)
        kali_vihje = models.CharField(max_length=255, blank=True)
        osa_tehtava = models.ForeignKey(Osatehtava)
        class Meta:
            db_table = u'tupa_syotemaarite'
        

        #end_legacy_class

class Syote(models.Model) :
        #gen_legacy_class Syote
        id = models.IntegerField(primary_key=True)
        arvo = models.CharField(max_length=255, blank=True)
        vartio = models.ForeignKey(Vartio, null=True, blank=True)
        maarite = models.ForeignKey(Syotemaarite)
        tarkistus = models.CharField(max_length=255, blank=True)
        class Meta:
            db_table = u'tupa_syote'
        

        #end_legacy_class

class Tuomarineuvostulos(models.Model) :
        #gen_legacy_class Tuomarineuvostulos
        id = models.IntegerField(primary_key=True)
        vartio = models.ForeignKey(Vartio)
        tehtava = models.ForeignKey(Tehtava)
        pisteet = models.CharField(max_length=255)
        class Meta:
            db_table = u'tupa_tuomarineuvostulos'
        

        #end_legacy_class

class Testaustulos(models.Model):
        #gen_legacy_class Testaustulos
        id = models.IntegerField(primary_key=True)
        vartio = models.ForeignKey(Vartio)
        tehtava = models.ForeignKey(Tehtava)
        pisteet = models.CharField(max_length=255)
        class Meta:
            db_table = u'tupa_testaustulos'
        

        #end_legacy_class

class Parametri(models.Model) :
        #gen_legacy_class Parametri
        id = models.IntegerField(primary_key=True)
        nimi = models.CharField(max_length=255)
        arvo = models.CharField(max_length=255)
        osa_tehtava = models.ForeignKey(Osatehtava)
        class Meta:
            db_table = u'tupa_parametri'
        

        #end_legacy_class
        
