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

    def setup(self):
        
        Testikisa = Kisa()
        Testikisa.nimi = "testikisa"
        Testikisa.save()
        
        Testisarja = Sarja()
        Testisarja.nimi = "valkoinen"
        Testisarja.Kisa = Testikisa
        Testisarja.save()
        
        Testivartio = Vartio()
        Testivartio.nimi = "trikoopellet"
        Testivartio.Sarja = Testivartio
        Testivartio.save()
        
        Testirasti = Rasti()
        Testirasti.nimi = "eka_testirasti"
        Testirasti.Sarja = Testirasti
        Testirasti.save()
        
        Testitehtava = Tehtava()
        Testitehtava.nimi = "ekatehtava"
        Testitehtava.Rasti = Testitehtava
        Testitehtava.kaava = "eka_syote_desimaaliluku+toka_syote_desimaaliluku" 
        Testitehtava.save()
        
        TestiSyoteMaarite1 = SyoteMaarite()
        TestiSyoteMaarite1.nimi = "eka_syote_desimaaliulku"
        TestiSyoteMaarite1.Tehtava = TestiSyoteMaarite1
        TestiSyoteMaarite1.save()
        
        TestiSyoteMaarite2 = SyoteMaarite()
        TestiSyoteMaarite2.nimi = "toka syote_desimaaliluku"
        TestiSyoteMaarite2.Tehtava = TestiSyoteMaarite2
        TestiSyoteMaarite2.save()
        
        TestiSyoteArvo1 = Syote()
        TestiSyoteArvo1.arvo = "5"
        TestiSyoteArvo1.Maarite = TestiSyoteMaarite1
        TestiSyoteMaarite1.vartio = Testivartio
        
        TestiSyoteArvo2 = Syote()
        TestiSyoteArvo2.arvo = "10"
        TestiSyoteArvo2.Maarite = TestiSyoteMaarite2
        TestiSyoteMaarite2.vartio = Testivartio
        
        
    def testlaskevartionpisteet(self):       
            LaskettavaSarja = Sarja.objects.all().filter(name="valkoinen").filter(kisa__nimi="testikisa")
            assert Laskin().laskeSarja(LaskettavaSarja) == "15"
        
        