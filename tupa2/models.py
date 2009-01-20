from django.db import models
# coding: latin-1


class Allergia(models.Model) :
    mille = models.CharField(maxlength=255,core=True)
    def __str__(self) :
        return self.mille
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Allergiat"

class Henkilo(models.Model) :
    nimi = models.CharField(maxlength=255)
    syntumavuosi = models.IntegerField(blank=True,null=True)
    lippukunta = models.CharField(maxlength=255,blank=True)
    jasennumero = models.CharField(maxlength=15,blank=True)
    vartio_nro = models.IntegerField(blank=True,null=True)
    puhelin_nro = models.CharField(maxlength=15,blank=True)
    homma = models.CharField(maxlength=255,blank=True)
    allergia =	models.ManyToManyField(Allergia ,null=True , blank=True)

    def __str__(self) :
        return self.nimi
    class Meta:
        verbose_name_plural = "Henkilöt"
    class Admin:
        pass


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
    maksimipisteet = models.FloatField(max_digits=5,decimal_places=2,core=True)
    vartion_maksimikoko = models.IntegerField(blank=True,null=True)
    vartion_minimikoko = models.IntegerField(blank=True,null=True)
    kisa = models.ForeignKey(Kisa,edit_inline=models.TABULAR)
    def __str__(self) :
        return self.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Sarjat"


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
    maksimipisteet = models.FloatField(decimal_places=2, max_digits=5)
    tehtavaryhma = models.CharField(maxlength=255,blank=True)
    tehavaluokka = models.CharField(maxlength=255,blank=True)
    rastikasky = models.TextField(blank=True)
    kaava = models.CharField(maxlength=255)
    rasti = models.ForeignKey(Rasti,edit_inline=models.STACKED)
    def __str__(self) :
        return self.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Tehtävät"


class Vartio(models.Model) :
    nimi = models.CharField(maxlength=255)
    kisa = models.ForeignKey(Kisa)
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

class Rata(models.Model) :
    sarja = models.ForeignKey(Sarja,edit_inline=models.TABULAR)
    rasti = models.ForeignKey(Rasti,core=True)
    jarjestysnro = models.IntegerField(core=True)
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Radat"


class Syote(models.Model) :
    nimi = models.CharField(maxlength=255,blank=True)
    kali_vihje = models.CharField(maxlength=255,blank=True)
    lyhenne = models.CharField(maxlength=255,core=True)
    arvo = models.FloatField(max_digits=20,decimal_places=4,null=True,blank=True)
    vartio = models.ForeignKey(Vartio,null=True,blank=True)
    tehtava = models.ForeignKey(Tehtava,edit_inline=models.TABULAR)
    parametri = models.BooleanField()
    def __str__(self) :
        return self.nimi
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Syötteet"


class Lopputulos(models.Model) :
    vartio = models.ForeignKey(Vartio,core=True)
    tehtava = models.ForeignKey(Tehtava,core=True,edit_inline=models.TABULAR)
    pisteet = models.FloatField(decimal_places=2, max_digits=5,core=True)
    list_display = ('vartio', 'tehtava')
    class Admin:
        pass
    class Meta:
        verbose_name_plural = "Lopputulokset"

