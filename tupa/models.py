from django.db import models

from random import uniform
from laskin import *
from django import newforms as forms

class Allergia(models.Model) :
    #gen_dia_class Allergia

    mille = models.CharField(maxlength=255)

    #end_dia_class
    def __str__(self) :
        return self.mille
    class Admin:
       pass
    class Meta:
        verbose_name_plural = "Allergiat"
    
    

class Kisa(models.Model) :
    #gen_dia_class Kisa

    nimi = models.CharField(maxlength=255)
    aika = models.DateField(blank=True, null=True )
    paikka = models.CharField(maxlength=255, blank=True )

    #end_dia_class
    def __str__(self) :
        return self.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Kisat"

class Sarja(models.Model) :
    #gen_dia_class Sarja

    nimi = models.CharField(maxlength=255)
    vartion_maksimikoko = models.IntegerField(blank=True, null=True, default=0 )
    vartion_minimikoko = models.IntegerField(blank=True, null=True,default=0 )
    kisa = models.ForeignKey(Kisa)

    #end_dia_class
    def __str__(self) :
        return self.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Sarjat"
    def laskeTulokset(self) :
        return Laskin().laskeSarja(self)

class Vartio(models.Model) :
    #gen_dia_class Vartio

    nimi = models.CharField(maxlength=255)
    nro = models.IntegerField()
    sarja = models.ForeignKey(Sarja)
    piiri = models.CharField(maxlength=255, blank=True )
    lippukunta = models.CharField(maxlength=255, blank=True )
    puhelinnro = models.CharField(maxlength=255, blank=True )
    sahkoposti = models.CharField(maxlength=255, blank=True )
    osoite = models.CharField(maxlength=255, blank=True )
    keskeyttanyt = models.IntegerField(blank=True, null=True )

    #end_dia_class
    def __str__(self) :
        return self.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Vartiot"

class Henkilo(models.Model) :
    #gen_dia_class Henkilo

    nimi = models.CharField(maxlength=255)
    syntumavuosi = models.IntegerField(blank=True , null=True )
    lippukunta = models.CharField(maxlength=255, blank=True, null=True )
    jasennumero = models.CharField(maxlength=15, blank=True, null=True )
    vartio_nro = models.IntegerField(blank=True, null=True )
    puhelin_nro = models.CharField(maxlength=15, blank=True, null=True )
    homma = models.CharField(maxlength=255, blank=True, null=True )

    #end_dia_class
    class Admin:
        pass
    def __str__(self) :
        return self.nimi
    class Meta:
        verbose_name_plural = "Henkilot"

class Rasti(models.Model) :
    #gen_dia_class Rasti

    nimi = models.CharField(maxlength=255)
    sarja = models.ForeignKey(Sarja)
    rastimiehet = models.ManyToManyField(Henkilo, blank=True )

    #end_dia_class
    def __str__(self) :
        return self.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Rastit"

class Tehtava(models.Model) :
    #gen_dia_class Tehtava

    nimi = models.CharField(maxlength=255)
    maksimipisteet = models.FloatField(decimal_places=2, max_digits=5, null=True, blank=True )
    tehtavaryhma = models.CharField(maxlength=255, blank=True )
    tehtavaluokka = models.CharField(maxlength=255, blank=True )
    rastikasky = models.TextField(blank=True )
    jarjestysnro = models.IntegerField(blank=True, null=True )
    kaava = models.CharField(maxlength=255)
    rasti = models.ForeignKey(Rasti)

    #end_dia_class

    def __str__(self) :
        return self.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Tehtavat"
    def mediaani(self,syotteen_nimi):
        syotteet=Syote.objects.filter(tehtava=self).filter(lyhenne=syotteen_nimi)
        arvot=[]
        for s in syotteet :
             if not s.arvo==None :
                 arvot.append( Decimal( str(s.arvo) ) )
        arvot.sort()
        if len(arvot) % 2 == 1:
            return arvot[(len(arvot)+1)/2-1]
        elif len(arvot):
            lower = arvot[len(arvot)/2-1]
            upper = arvot[len(arvot)/2]
            return (lower + upper) / 2  
        else :
            return None

class Rata(models.Model) :
    #gen_dia_class Rata

    sarja = models.ForeignKey(Sarja)
    rasti = models.ForeignKey(Rasti)
    jarjestysnro = models.IntegerField()

    #end_dia_class

    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Radat"

class SyoteMaarite(models.Model) :
    #gen_dia_class SyoteMaarite

    nimi = models.CharField(maxlength=255)
    tyyppi = models.CharField(maxlength=255)
    kali_vihje = models.CharField(maxlength=255)
    tehtava = models.ForeignKey(Tehtava)

    #end_dia_class
    def __str__(self) :
        return self.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Syotteen maaritteet"

class Syote(models.Model) :
    #gen_dia_class Syote

    arvo = models.CharField(maxlength=255)
    vartio = models.ForeignKey(Vartio, blank=True )
    maarite = models.ForeignKey(SyoteMaarite)

    #end_dia_class

    def __str__(self) :
        return self.vartio.nimi + " " + self.maarite.nimi + " " + self.maarite.tehtava.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Syotteet"

class Lopputulos(models.Model) :
    #gen_dia_class Lopputulos

    vartio = models.ForeignKey(Vartio)
    tehtava = models.ForeignKey(Tehtava)
    pisteet = models.FloatField(decimal_places=2, max_digits=5 )

    #end_dia_class
    def __str__(self) :
        return self.tehtava.nimi + " " + self.vartio.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Lopputulokset"

class Syotatulos(models.Model):

    kisa = models.CharField(maxlength=255, help_text='Mille kisalle?')
    sarja = models.CharField(maxlength=255, help_text='Mille sarjalle?')
    tehtavaNro = models.IntegerField(help_text='Mihin tehtavaan?')
    class Admin:
        pass

    def __str__(self):
        return self.tehtava


