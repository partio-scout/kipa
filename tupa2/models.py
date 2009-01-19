from django.db import models


class Henkilo(models.Model) :
    nimi = models.CharField(maxlength=255)
    syntumavuosi = models.IntegerField()
    lippukunta = models.CharField(maxlength=255)
    jasennumero = models.CharField(maxlength=15)
    vartio_nro = models.IntegerField()
    puhelin_nro = models.CharField(maxlength=15)
    homma = models.CharField(maxlength=255)
    def __str__(self) :
        return self.nimi
    class Admin:
        pass


class Kisa(models.Model) :
    nimi = models.CharField(maxlength=255)
    aika = models.DateField()
    paikka = models.CharField(maxlength=255)
    def __str__(self) :
        return self.nimi
    class Admin:
        pass


class Tehtava(models.Model) :
    nimi = models.CharField(maxlength=255)
    maksimipisteet = models.FloatField(decimal_places=2, max_digits=5)
    tehtavaryhma = models.CharField(maxlength=255)
    tehavaluokka = models.CharField(maxlength=255)
    rastikasky = models.TextField()
    jarjestysnro = models.IntegerField()
    kaava = models.CharField(maxlength=255)
    def __str__(self) :
        return self.nimi
    class Admin:
        pass


class Sarja(models.Model) :
    nimi = models.CharField(maxlength=255)
    maksimipisteet = models.FloatField(max_digits=5,decimal_places=2)
    vartion_maksimikoko = models.IntegerField()
    vartion_minimikoko = models.IntegerField()
    kisa = models.ForeignKey(Kisa)
    def __str__(self) :
        return self.nimi
    class Admin:
        pass


class Rasti(models.Model) :
    nimi = models.CharField(maxlength=255)
    sarja = models.ForeignKey(Sarja)
    rastimiehet = models.ManyToManyField(Henkilo)
    def __str__(self) :
        return self.nimi
    class Admin:
        pass


class Allergia(models.Model) :
    mille = models.CharField(maxlength=255)
    henkilo = models.ForeignKey(Henkilo)
    def __str__(self) :
        return self.mille
    class Admin:
        pass


class Vartio(models.Model) :
    nimi = models.CharField(maxlength=255)
    kisa = models.ForeignKey(Kisa)
    sarja = models.ForeignKey(Sarja)
    piiri = models.CharField(maxlength=255)
    lippukunta = models.CharField(maxlength=255)
    puhelinnro = models.CharField(maxlength=255)
    sahkoposti = models.CharField(maxlength=255)
    osoite = models.CharField(maxlength=255)
    keskeyttanyt = models.IntegerField()
    def __str__(self) :
        return self.nimi
    class Admin:
        pass


class Rata(models.Model) :
    sarja = models.ForeignKey(Sarja)
    rasti = models.ForeignKey(Rasti)
    jarjestysnro = models.IntegerField()
    class Admin:
        pass


class Syote(models.Model) :
    nimi = models.CharField(maxlength=255)
    kali_vihje = models.CharField(maxlength=255)
    lyhenne = models.CharField(maxlength=255)
    arvo = models.FloatField(max_digits=5,decimal_places=2)
    vartio = models.ForeignKey(Vartio)
    tehtava = models.ForeignKey(Tehtava)
    parametri = models.BooleanField()
    def __str__(self) :
        return self.nimi
    class Admin:
        pass


class Lopputulos(models.Model) :
    vartio = models.ForeignKey(Vartio)
    tehtava = models.ForeignKey(Tehtava)
    pisteet = models.FloatField(decimal_places=2, max_digits=5)
    class Admin:
        pass

