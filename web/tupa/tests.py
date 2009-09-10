#coding=latin_1
import unittest

from models import *
from AritmeettinenLaskin import *
from TulosLaskin import *
import decimal
from django.test import TestCase
from views import *
import os
from django.test.client import Client
from django.http import HttpRequest

class aritmeettinen_laskin_test(unittest.TestCase):
    """
    Peruslaskimen unit testit
    """
    def testYhteenlasku(self):
        assert    laske('5+5') == '10'
    
    def testYhteenlasku_spacet(self):
        assert    laske(' 5 + 5 ') == '10'
    
    def testDesimaaliluku(self):
        assert    Decimal(laske('0.5*2+10.5000')) == Decimal('11.5000')
    
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
        
    #def testkaksimiinusmerkkia(self):
        #assert    laske('5+2--5') == None
        
    #def testplusmiinus(self):
        #assert    laske('5+2+-5') == None 
      
    def testkertojako(self):
        assert    laske('5+2*/5') == None

    def testLaskettuNegatiivinenOperandi(self):
        assert    laske('3*(1-5)') == "-12"
    def testTuotosPotenssimuoto(self):
        assert not laske('-0.008333333333333333333333333333*0.0') == None


def haeTulos(sarjanTulokset, vartio, tehtava) :
    """
    Hakee Vartion pisteet tehtävälle määritellystä tulostaulukosta
    """
    for vart_nro in range(1,len(sarjanTulokset)-1) :
        for teht_nro in range(2,len(sarjanTulokset[vart_nro])):
            tulokset =sarjanTulokset[vart_nro][teht_nro]
            if sarjanTulokset[vart_nro][0] ==vartio and sarjanTulokset[0][teht_nro] ==tehtava:
                 return tulokset

def ViewSanityCheck(fixture_name):
        """
        Luo tescasen tarkistamaan sen etta kaikki nakumat toimivat kaatumatta.
        fixture name = tietokantafixtuurin nimi jolle testi luodaan.
        palauttaa TestCase:n
        """
        class testi(TestCase) :
                fixtures = [fixture_name]
                def testTulokset(self):
                        """
                        Ajaa jokaisen nakyman testidatalla
                        Testi antaa virheen jos jokin nakuma kaatuu.
                        """
                        kisat=Kisa.objects.all()
                        sarjat=Sarja.objects.all()
                        tehtavat=Tehtava.objects.all()
                        virheet=[]
                        request =HttpRequest()
                        tietokantaan(request)
                        maaritaKisa(request)
                        for k in kisat :
                                kisa_nimi=k.nimi
                                kisa(request,kisa_nimi=kisa_nimi)
                                maaritaKisa(request,kisa_nimi=kisa_nimi)
                                maaritaValitseTehtava(request,kisa_nimi=kisa_nimi)
                                maaritaVartiot(request,kisa_nimi=kisa_nimi)
                                testiTulos(request,kisa_nimi=kisa_nimi)
                                syotaKisa(request,kisa_nimi=kisa_nimi)
                                tulosta(request,kisa_nimi=kisa_nimi)
                        for s in sarjat:
                                sarja_id=s.id
                                kisa_nimi=s.kisa.nimi
                                maaritaTehtava(request,kisa_nimi=kisa_nimi,sarja_id=sarja_id)
                                kopioiTehtavia(request,kisa_nimi=kisa_nimi,sarja_id=sarja_id)
                                tulostaSarja(request,kisa_nimi=kisa_nimi, sarja_id=sarja_id)
                        for t in tehtavat:
                                tehtava_id=t.id
                                kisa_nimi=t.sarja.kisa.nimi
                                maaritaTehtava(request,kisa_nimi=kisa_nimi,tehtava_id=tehtava_id)
                                syotaTehtava(request,kisa_nimi=kisa_nimi,tehtava_id=tehtava_id)
        return testi



def TulosTestFactory(fixture_name):
        """
        Tekee tulostestin halutulle tietokanta fixtuurille.
        fixture_name = fixtuurin nimi jolle testi tehdaan.
        palauttaa TestCase:n
        """
        class testi(TestCase) :
                fixtures = [fixture_name]
                def testTulokset(self):
                        """
                        Iteroi jokaisen sarjan ja tehtavan.
                        Laskee tulokset ja vertaa tuloksia maariteltyihin testituloksiin.
                        Tunnistaa laskennan kaatavia virheita.
                        Tunnistaa vaarat tulokset.
                        Vaarien tulosten kohdalla tulostaa yhteenvedon.
                        """
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
                                                for s in Syote.objects.filter(maarite__osa_tehtava__tehtava=t.tehtava).filter(vartio=t.vartio):
                                                        ilmoitus=ilmoitus + s.maarite.nimi+"="+ s.arvo + " "
                                                ilmoitus=ilmoitus + "\nKaava: " + t.tehtava.kaava
                                                ilmoitus=ilmoitus + "\nOstatehtavien kaavat: " 
                                                for k in OsaTehtava.objects.filter(tehtava=t.tehtava):
                                                        ilmoitus=ilmoitus + "\n    "+k.nimi +"="+ k.kaava + " "
                                                ilmoitus=ilmoitus + "\nVartio: "  + t.vartio.nimi  
                                                ilmoitus=ilmoitus + "\nTulos: "   + str(tulos)+' != '+str(vaadittava)
                                                virheet.append(ilmoitus) 
                        virhe= str(len(virheet)) + " errors"
                        for v in virheet:
                                virhe=virhe + "\n--------------------------------\n" + v 
                        self.failUnless( len(virheet) == 0 , unicode(virhe).encode('ascii', 'replace')
)
        return testi

testit=[aritmeettinen_laskin_test]

# haetaan kaikki xml fixtuurien nimet.
test_fixtures=[]
for f in os.listdir(os.curdir+"/fixtures/tests/"):
        if not f.find(".xml") == -1:
                test_fixtures.append("fixtures/tests/"+f)

# luodaan tulostestit fixtuureista.
for t in test_fixtures:
        testit.append( TulosTestFactory(t) )
# luodaan viewtestit fixtuureista.
for t in test_fixtures:
        testit.append( ViewSanityCheck(t) )

# luodaan testsuite jossa on kaikki testit.
def suite():
        suites = [] 
        for t in testit :
                suites.append(unittest.TestLoader().loadTestsFromTestCase(t))
        suite=unittest.TestSuite(suites)
        return suite


