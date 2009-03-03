#coding=latin_1
import unittest

from models import *
from peruslaskin import *
from laskin import *

class peruslaskin_test(unittest.TestCase):
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
        laskia = Laskin()
        a.arvo=5
        b.arvo=2
        perusTehtava.kaava="a+b"
        assert  laskia.laskePisteet([a,b],perusTehtava) == '7'
    
   

class tietokanta_test(unittest.TestCase):

    """
    Testataan laskimen kykyä ronkkia tietokantaa ja laskea saatu data järkevästi. Setupissa määritellään testitietokanta jota käytetään kaikissa muissa testeissä.
    """

    def setUp(self):
        Testikisa = Kisa(nimi="testikisa")
        Testikisa.save()
        
        Testisarja = Sarja(nimi="valkoinen",kisa=Testikisa)
        Testisarja.save()
        
        Testivartio = Vartio()
        Testivartio.nimi = "trikoopellet"
        Testivartio.nro = 1
        Testivartio.sarja = Testisarja
        Testivartio.save()
        
        Testirasti = Rasti()
        Testirasti.nimi = "eka_testirasti"
        Testirasti.sarja = Testisarja
        Testirasti.save()
        
        Testitehtava = Tehtava()
        Testitehtava.nimi = "ekatehtava"
        Testitehtava.rasti = Testirasti
        Testitehtava.jarjestysnro = 1
        Testitehtava.kaava = "eka_syote_desimaaliluku+toka_syote_desimaaliluku" 
        Testitehtava.save()
        
        TestiSyoteMaarite1 = SyoteMaarite()
        TestiSyoteMaarite1.nimi = "eka_syote_desimaaliluku"
        TestiSyoteMaarite1.tehtava = Testitehtava
        TestiSyoteMaarite1.save()
        
        TestiSyoteMaarite2 = SyoteMaarite()
        TestiSyoteMaarite2.nimi = "toka_syote_desimaaliluku"
        TestiSyoteMaarite2.tehtava = Testitehtava
        TestiSyoteMaarite2.save()
        
        TestiSyoteArvo1 = Syote()
        TestiSyoteArvo1.arvo = "5"
        TestiSyoteArvo1.maarite = TestiSyoteMaarite1
        TestiSyoteArvo1.vartio = Testivartio
        TestiSyoteArvo1.save()

        TestiSyoteArvo2 = Syote()
        TestiSyoteArvo2.arvo = "10"
        TestiSyoteArvo2.maarite = TestiSyoteMaarite2
        TestiSyoteArvo2.vartio = Testivartio
        TestiSyoteArvo2.save()
        
        
    def testlaskevartionpisteet(self):       
        LaskettavaSarja = Sarja.objects.filter(nimi="valkoinen").filter(kisa__nimi="testikisa")[0]
        tulokset = Laskin().laskeSarja(LaskettavaSarja) 
        assert tulokset[1][1]== "15"
        
        
