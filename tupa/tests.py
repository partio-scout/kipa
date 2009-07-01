#coding=latin_1
import unittest

from models import *
from AritmeettinenLaskin import *
from TulosLaskin import *
import decimal
from django.test import TestCase

import os

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
    def testTuntematonVirheA(self):
        assert not laske('-0.008333333333333333333333333333*0.0') == None

def haeTulos(sarjanTulokset, vartio, tehtava) :
    """
    Hakee Vartion pisteet tehtävälle määritellystä tulostaulukosta
    """
    for vart_nro in range(1,len(sarjanTulokset)-1) :
        for teht_nro in range(2,len(sarjanTulokset[vart_nro])-1):
            tulokset =sarjanTulokset[vart_nro][teht_nro]
            if sarjanTulokset[vart_nro][0] ==vartio and sarjanTulokset[0][teht_nro] ==tehtava:
                 return tulokset

def TulosTestFactory(fixture_name):
        class testi(TestCase) :
                fixtures = [fixture_name]
                def testTulokset(self):
                        self.sarjat=Sarja.objects.all()
                        virheet=[]
                        for s in self.sarjat:
                                virheilmoitus=""
                                for f in self.fixtures:
                                        virheilmoitus=virheilmoitus+f+" " 
                                        
                                virheilmoitus=virheilmoitus+"\nSarja: "+s.nimi+""
                                self.testausTulokset=TestausTulos.objects.filter(tehtava__sarja=s)
                                tulokset=s.laskeTulokset()
                                for t in self.testausTulokset :
                                        tulos=haeTulos(tulokset,t.vartio,t.tehtava)
                                        vaadittava = t.pisteet
                                        if not tulos==None and is_number(tulos):
                                               tulos = Decimal(tulos)
                                        if not vaadittava==None and is_number(vaadittava):
                                                vaadittava = Decimal(vaadittava)
                                        if not tulos == vaadittava:
                                                ilmoitus= virheilmoitus
                                                ilmoitus=ilmoitus + "\nTehtava: " + t.tehtava.nimi
                                                ilmoitus=ilmoitus + "\nSyotteet: "
                                                for s in Syote.objects.filter(maarite__tehtava=t.tehtava).filter(vartio=t.vartio):
                                                        ilmoitus=ilmoitus + s.maarite.nimi+"="+ s.arvo + " "
                                                ilmoitus=ilmoitus + "\nKaava: " + t.tehtava.kaava
                                                ilmoitus=ilmoitus + "\nOstatehtavien kaavat: " 
                                                for k in OsapisteKaava.objects.filter(tehtava=t.tehtava):
                                                        ilmoitus=ilmoitus + k.nimi +"="+ k.kaava + " "
                                                ilmoitus=ilmoitus + "\nVartio: "  + t.vartio.nimi  
                                                ilmoitus=ilmoitus + "\nTulos: "   + str(tulos)+' != '+str(vaadittava)
                                                virheet.append(ilmoitus) 
                        virhe= str(len(virheet)) + " errors"
                        for v in virheet:
                                virhe=virhe + "\n--------------------------------\n" + v 
                        print virhe
                        self.failUnless( len(virheet) == 0 , unicode(virhe).encode('ascii', 'replace')
)
        return testi

testit=[aritmeettinen_laskin_test]

# haetaan kaikki xml fixtuurien nimet.
test_fixtures=[]
for f in os.listdir(os.curdir+"/tupa/fixtures/tests/"):
        if not f.find(".xml") == -1:
                test_fixtures.append("tests/"+f)

# luodaan tulostestit fixtuureista.
for t in test_fixtures:
        print t
        testit.append( TulosTestFactory(t) )

# luodaan testsuite jossa on kaikki testit.
def suite():
        suites = [] 
        for t in testit :
                suites.append(unittest.TestLoader().loadTestsFromTestCase(t))
        suite=unittest.TestSuite(suites)
        return suite


