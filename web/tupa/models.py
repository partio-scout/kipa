from django.db import models

from random import uniform
from TulosLaskin import *

class Allergia(models.Model) :
    #gen_dia_class Allergia

    mille = models.CharField(max_length=255)

    #end_dia_class
    def __str__(self) :
        return self.mille
    class Meta:
        verbose_name_plural = "Allergiat"

class Kisa(models.Model) :
    #gen_dia_class Kisa

    nimi = models.CharField(max_length=255)
    aika = models.DateField(blank=True, null=True )
    paikka = models.CharField(max_length=255, blank=True )

    #end_dia_class
    def __str__(self) :
        return self.nimi
    class Meta:
        verbose_name_plural = "Kisat"

class Sarja(models.Model) :
    #gen_dia_class Sarja

    nimi = models.CharField(max_length=255)
    vartion_maksimikoko = models.IntegerField(blank=True, null=True, default=0 )
    vartion_minimikoko = models.IntegerField(blank=True, null=True,default=0 )
    kisa = models.ForeignKey(Kisa)

    #end_dia_class
    def __str__(self) :
        return self.nimi
    class Meta:
        verbose_name_plural = "Sarjat"
    def laskeTulokset(self) :
        return TulosLaskin().laskeSarja(self)

class Vartio(models.Model) :
    #gen_dia_class Vartio

    nro = models.IntegerField()
    nimi = models.CharField(max_length=255)
    sarja = models.ForeignKey(Sarja)
    piiri = models.CharField(max_length=255, blank=True )
    lippukunta = models.CharField(max_length=255, blank=True )
    puhelinnro = models.CharField(max_length=255, blank=True )
    sahkoposti = models.CharField(max_length=255, blank=True )
    osoite = models.CharField(max_length=255, blank=True )
    keskeyttanyt = models.IntegerField(blank=True, null=True )
    ulkopuolella = models.IntegerField(blank=True , null=True )

    #end_dia_class
    def __str__(self) :
        return self.nimi
    class Meta:
        verbose_name_plural = "Vartiot"

class Henkilo(models.Model) :
    #gen_dia_class Henkilo

    nimi = models.CharField(max_length=255)
    syntymavuosi = models.IntegerField(blank=True , null=True )
    lippukunta = models.CharField(max_length=255, blank=True, null=True )
    jasennumero = models.CharField(max_length=15, blank=True, null=True )
    puhelin_nro = models.CharField(max_length=15, blank=True, null=True )
    homma = models.CharField(max_length=255, blank=True, null=True )

    #end_dia_class
    def __str__(self) :
        return self.nimi
    class Meta:
        verbose_name_plural = "Henkilot"

class Rasti(models.Model) :
    #gen_dia_class Rasti

    nimi = models.CharField(max_length=255)
    sarja = models.ForeignKey(Sarja)
    rastimiehet = models.ManyToManyField(Henkilo, blank=True )

    #end_dia_class
    def __str__(self) :
        return self.sarja.nimi + " " + self.nimi
    class Meta:
        verbose_name_plural = "Rastit"


class Tehtava(models.Model) :
    #gen_dia_class Tehtava

    nimi = models.CharField(max_length=255)
    maksimipisteet = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=10 )
    tehtavaryhma = models.CharField(max_length=255, blank=True )
    tehtavaluokka = models.CharField(max_length=255, blank=True )
    rastikasky = models.TextField(blank=True )
    jarjestysnro = models.IntegerField()
    kaava = models.CharField(max_length=255)
    sarja = models.ForeignKey(Sarja)

    #end_dia_class
    def __str__(self) :
        return self.nimi
    class Meta:
        verbose_name_plural = "Tehtavat"

    def suurin(self,syotteen_nimi) :
        syotteet=Syote.objects.filter(maarite__tehtava=self).filter(maarite__nimi=syotteen_nimi)
        suurin=None
        if syotteet :
            for s in syotteet :
                arvo = stringDecimaaliksi(s.arvo)
                if not s.vartio.ulkopuolella == None and s.maarite.tehtava.jarjestysnro <= s.vartio.ulkopuolella :
                    pass #Vartio on ulkopuolella joten se on poissa hausta.
                elif arvo==None :
                    pass #
                elif suurin ==None :
                    suurin = arvo
                elif arvo > suurin :
                    suurin = arvo
        return suurin

    def pienin(self,syotteen_nimi) :
        syotteet=Syote.objects.filter(maarite__tehtava=self).filter(maarite__nimi=syotteen_nimi)
        pienin=None
        if syotteet :
            for s in syotteet :
                arvo = stringDecimaaliksi(s.arvo)
                if not s.vartio.ulkopuolella == None and s.maarite.tehtava.jarjestysnro <= s.vartio.ulkopuolella :
                    pass #Vartio on ulkopuolella joten se on poissa hausta.
                elif arvo==None :
                    pass #
                elif pienin==None :
                    pienin = arvo
                elif arvo < pienin :
                    pienin = arvo
                    
        return pienin

    def mediaani(self,syotteen_nimi):
        syotteet=Syote.objects.filter(maarite__tehtava=self).filter(maarite__nimi=syotteen_nimi)
        arvot=[]
        if syotteet:
            for s in syotteet :
	        if not s.vartio.ulkopuolella == None and s.maarite.tehtava.jarjestysnro <= s.vartio.ulkopuolella:
                    pass #Vartio on ulkopuolella joten se on poissa mediaanista.
                elif not s.arvo==None :
                    arvot.append(stringDecimaaliksi(s.arvo) ) 
        
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

    class Meta:
        verbose_name_plural = "Radat"

class SyoteMaarite(models.Model) :
    TYYPPI_VAIHTOEHDOT = (
        ('aika', 'aika'),
        ('piste', 'piste'),
    )

    #gen_dia_class SyoteMaarite

    nimi = models.CharField(max_length=255)
    tyyppi = models.CharField(max_length=255, choices=TYYPPI_VAIHTOEHDOT )
    kali_vihje = models.CharField(max_length=255, blank=True , null=True )
    tehtava = models.ForeignKey(Tehtava)

    #end_dia_class
    def __str__(self) :
        return self.nimi
    class Meta:
        verbose_name_plural = "Syotteen maaritteet"

class Syote(models.Model) :
    #gen_dia_class Syote

    arvo = models.CharField(max_length=255)
    vartio = models.ForeignKey(Vartio, blank=True, null=True )
    maarite = models.ForeignKey(SyoteMaarite)

    #end_dia_class

    def __str__(self) :
        return self.vartio.nimi     
    class Meta:
        verbose_name_plural = "Syotteet"

class TuomarineuvosTulos(models.Model) :
    #gen_dia_class TuomarineuvosTulos

    vartio = models.ForeignKey(Vartio)
    tehtava = models.ForeignKey(Tehtava)
    pisteet = models.DecimalField(decimal_places=2, max_digits=5 )

    #end_dia_class
    def __str__(self) :
        return self.tehtava.nimi + " " + self.vartio.nimi
    class Meta:
        verbose_name_plural = "Tuomarineuvoston tulokset"


class OsapisteKaava(models.Model) :
    #gen_dia_class OsapisteKaava

    kaava = models.CharField(max_length=255)
    tehtava = models.ForeignKey(Tehtava)

    #end_dia_class
    def __str__(self) :
        return self.kaava
    class Meta:
        verbose_name_plural = "Osapisteiden kaavat"



