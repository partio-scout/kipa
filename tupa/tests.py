#coding=latin_1
import unittest

from models import *
from AritmeettinenLaskin import *
from TulosLaskin import *
import decimal

class aritmeettinen_laskin_test(unittest.TestCase):
    """
    Peruslaskimen unit testit

    """
    def testYhteenlasku(self):
        assert    laske('5+5') == '10'
    
    def testYhteenlasku_spacet(self):
        assert    laske(' 5 + 5 ') == '10'
    
    def testDesimaaliluku(self):
        assert    laske('0.5*2+10.5000') == '11.5000'
    
    def testMuuttujavirhe(self):
        assert    laske('tyhja_muuttuja*5') == None

    def testSulkulauseke(self):
        assert    laske('2*(1+9)') == '20'

    def testSulut_sisakkain(self):
        assert    laske('10*((1+2)+(5*10))') == '530'

    def testSulut_vaarinpain(self):
        assert    laske('10*)(1+2)+(5*10))') == None

    def testSulut_vaaramaara(self):
        assert    laske('10*(1+2)+(5*10))') == None

    def testNollallajako(self):
        assert    laske('10/0') == None
        
    def testTyhjasyote(self):
        assert    laske('') == None
        
    def testEiaritmtetiikkaa(self):
        assert    laske('a+ b-c*d') == None
    
    def testkaksikertomerkkia(self):
        assert    laske('5+2**5') == None
     
    def testkaksiplusmerkkia(self):
        assert    laske('5+2++5') == None
        
    def testkaksimiinusmerkkia(self):
        assert    laske('5+2--5') == None
        
    def testplusmiinus(self):
        assert    laske('5+2+-5') == None 
      
    def testkertojako(self):
        assert    laske('5+2*/5') == None

    def testLaskettuNegatiivinenOperandi(self):
        assert    laske('3*(1-5)') == "-12"

       
class lasketulos_test(unittest.TestCase):
    """
    Laskimen lasketulos luokan (eli ns. pÃ¤Ã¤tason) unit testit
    """
    def testLaske_muuttujat(self):
        perusKisa=Kisa()
        perusKisa.nimi="Peruskisa"
        perusKisa.save()
        perusSarja = Sarja()
        perusSarja.kisa=perusKisa
        perusSarja.nimi="PerusSarja"
        perusSarja.save()
        perusRasti = Rasti()
        perusRasti.sarja=perusSarja
        perusRasti.nimi="PerusRasti"
        perusRasti.save()
        perusTehtava = Tehtava()
        perusTehtava.rasti=perusRasti
        perusTehtava.nimi="PerusTehtava"
        perusTehtava.save()
        a = Syote()
        b = Syote()
        maariteA=SyoteMaarite()
        maariteB=SyoteMaarite()
        maariteA.nimi = "a"
        maariteB.nimi = "b"
        maariteA.tehtava = perusTehtava
        maariteB.tehtava = perusTehtava
        maariteA.save()
        maariteB.save()
        a.maarite=maariteA
        b.maarite=maariteB
        a.save()
        b.save()
        laskia = TulosLaskin()
        a.arvo=5
        b.arvo=2
        perusTehtava.kaava="a+b"
        assert  laskia.laskePisteet([a,b],perusTehtava) == '7'
    
   

def haeTulos(sarjanTulokset, vartio, tehtava) :
    """
    Hakee Vartion pisteet tehtävälle määritellystä tulostaulukosta
    """
    for vart_nro in range(len(sarjanTulokset)-1) :
        for teht_nro in range(len(sarjanTulokset[0])-1):
            tulokset =sarjanTulokset[vart_nro+1][teht_nro+1]
            if sarjanTulokset[vart_nro+1][0] ==vartio and sarjanTulokset[0][teht_nro+1] ==tehtava:
                 return tulokset

class tietokanta_test(unittest.TestCase):
    """
    Testataan laskimen kykyä ronkkia tietokantaa ja laskea saatu data järkevästi. Setupissa määritellään testitietokanta jota käytetään kaikissa muissa testeissä.
    """
    fixtures = ['laskenta_tests.xml']
    def setUp(self):
        sarja=Sarja.objects.filter(nimi="Funktiot")[0]
        self.parasVartio=Vartio.objects.filter(nimi="ParasVartio")[0]
        self.keskimmainenVartio=Vartio.objects.filter(nimi="KeskimmainenVartio")[0]
        self.huonoinVartio=Vartio.objects.filter(nimi="HuonoinVartio")[0]
        self.tulokset=sarja.laskeTulokset()
    
    def testInterpoloiAika(self):
        tehtava= Tehtava.objects.filter(nimi="interpoloi_aika")[0]
        assert Decimal(haeTulos(self.tulokset,self.parasVartio,tehtava)) == Decimal("5")
        assert Decimal(haeTulos(self.tulokset,self.keskimmainenVartio,tehtava)) == Decimal("2.50")
        assert Decimal(haeTulos(self.tulokset,self.huonoinVartio,tehtava)) == Decimal("0")
    def testInterpoloiPisteet(self):
        tehtava= Tehtava.objects.filter(nimi="interpoloi_pisteet")[0]
        assert Decimal(haeTulos(self.tulokset,self.parasVartio,tehtava)) == Decimal("5")
        assert Decimal(haeTulos(self.tulokset,self.keskimmainenVartio,tehtava)) == Decimal("2.50")
        assert Decimal(haeTulos(self.tulokset,self.huonoinVartio,tehtava)) == Decimal("0")
        
     
        
