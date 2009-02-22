from django.db import models

from random import uniform
from laskin import *
from django import newforms as forms


class Allergia(models.Model) :
    mille = models.CharField(maxlength=255)
    def __str__(self) :
        return self.mille
    class Admin:
       pass
    class Meta:
        verbose_name_plural = "Allergiat"
    
    

class Kisa(models.Model) :
    nimi = models.CharField(maxlength=255)
    aika = models.DateField(blank=True,null=True)
    paikka = models.CharField(maxlength=255,blank=True)
    def __str__(self) :
        return self.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Kisat"

class Sarja(models.Model) :
    nimi = models.CharField(maxlength=255,core=True)
    vartion_maksimikoko = models.IntegerField(blank=True,null=True)
    vartion_minimikoko = models.IntegerField(blank=True,null=True)
    kisa = models.ForeignKey(Kisa,edit_inline=models.TABULAR)
    def __str__(self) :
        return self.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Sarjat"
    def laskeTulokset(self) :
        return Laskin().laskeSarja(self)

class Vartio(models.Model) :
    nimi = models.CharField(maxlength=255)
    nro = models.IntegerField()
    sarja = models.ForeignKey(Sarja)
    piiri = models.CharField(maxlength=255,blank=True)
    lippukunta = models.CharField(maxlength=255,blank=True)
    puhelinnro = models.CharField(maxlength=255,blank=True)
    sahkoposti = models.CharField(maxlength=255,blank=True)
    osoite = models.CharField(maxlength=255,blank=True)
    keskeyttanyt = models.IntegerField(null=True,blank=True)
    def __str__(self) :
        return self.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Vartiot"

class Henkilo(models.Model) :
    nimi = models.CharField(maxlength=255)
    syntymavuosi = models.IntegerField(blank=True,null=True)
    lippukunta = models.CharField(maxlength=255,blank=True)
    jasennumero = models.CharField(maxlength=15,blank=True)
    vartio= models.ForeignKey(Vartio,blank=True,null=True)
    puhelin_nro = models.CharField(maxlength=15,blank=True)
    homma = models.CharField(maxlength=255,blank=True)
    allergia =	models.ManyToManyField(Allergia ,null=True , blank=True)
    class Admin:
        pass
    def __str__(self) :
        return self.nimi
    class Meta:
        verbose_name_plural = "Henkilot"

class Rasti(models.Model) :
    nimi = models.CharField(maxlength=255,core=True)
    sarja = models.ForeignKey(Sarja,edit_inline=models.TABULAR)
    rastimiehet = models.ManyToManyField(Henkilo,blank=True)
    def __str__(self) :
        return self.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Rastit"

class Tehtava(models.Model) :
    nimi = models.CharField(maxlength=255,core=True)
    tehtavaryhma = models.CharField(maxlength=255,blank=True)
    tehtavaluokka = models.CharField(maxlength=255,blank=True)
    rastikasky = models.TextField(blank=True)
    jarjestysnro = models.IntegerField()
    kaava = models.CharField(maxlength=255)
    rasti = models.ForeignKey(Rasti,edit_inline=models.STACKED)
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
    sarja = models.ForeignKey(Sarja,edit_inline=models.TABULAR)
    rasti = models.ForeignKey(Rasti,core=True)
    jarjestysnro = models.IntegerField(core=True)
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Radat"

class SyoteMaarite(models.Model) :
    nimi = models.CharField(maxlength=255,blank=True)
    kali_vihje = models.CharField(maxlength=255,blank=True)
    tyyppi = models.CharField(maxlength=255,core=True)
    tehtava = models.ForeignKey(Tehtava,edit_inline=models.TABULAR)
    def __str__(self) :
        return self.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Syotteen maaritteet"

class Syote(models.Model) :
    arvo = models.CharField(maxlength=255,blank=True)
    vartio = models.ForeignKey(Vartio,null=True,blank=True)
    maarite = models.ForeignKey(SyoteMaarite)
    def __str__(self) :
        return self.vartio.nimi + " " + self.maarite.nimi + " " + self.maarite.tehtava.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Syotteet"

class Lopputulos(models.Model) :
    vartio = models.ForeignKey(Vartio)
    tehtava = models.ForeignKey(Tehtava)
    pisteet = models.FloatField(decimal_places=2, max_digits=5,null=True,blank=True)
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


