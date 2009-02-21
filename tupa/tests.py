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
        assert  laske('5+5') == '10'
    
    def testYhteenlasku_spacet(self):
        assert  laske(' 5 + 5 ') == '10'
    
    def testDesimaaliluku(self):
        assert  laske('0.5*2+10.5000') == '11.5'
    
    def testMuuttujavirhe(self):
        assert  laske('tyhja_muuttuja*5') == None

    def testSulkulauseke(self):
        assert  laske('2*(1+9)') == '20'

    def testSulut_sisakkain(self):
        assert  laske('10*((1+2)+(5*10))') == '530'

    def testSulut_vaarinpain(self):
        assert  laske('10*)(1+2)+(5*10))') == None

    def testSulut_vaaramaara(self):
        assert  laske('10*(1+2)+(5*10))') == None

    def testNollallajako(self):
        assert  laske('10/0') == None 

     
class lasketulos_test(unittest.TestCase):

    """
    Laskimen lasketulos luokan (eli ns. pÃ¤Ã¤tason) unit testit
    """

    def testLaske_muuttujat(self):
        perusTehtava = Tehtava()
        a = Syote()
        b = Syote()
        laskia = Laskin()
        a.lyhenne= "a"
        a.arvo=5
        b.lyhenne= "b"
        b.arvo=2
        perusTehtava.kaava="a+b"
        assert  laskia.laskeTulos([a,b],perusTehtava) == '7'

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
       
        
        
