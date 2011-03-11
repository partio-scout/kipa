# encoding: utf-8
# KiPa(KisaPalvelu), tuloslaskentaj‰rjestelm‰ partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi

import unittest

from models import *
from taulukkolaskin import *
import decimal
from django.test import TestCase
from views import *
import os
from django.test.client import Client
from django.http import HttpRequest,QueryDict

def is_number(s):
        if not s : return False
        try: float(s)
        except ValueError: return False
        return True

class aritmeettinen_laskin_test(unittest.TestCase):
    """
    Peruslaskimen unit testit
    """
    def testYhteenlasku(self):
        assert    laske('5+5') == Decimal('10')
    
    def testYhteenlasku_spacet(self):
        assert    laske(' 5 + 5 ') == Decimal('10')
    
    def testDesimaaliluku(self):
        assert    Decimal(laske('0.5*2+10.5000')) == Decimal('11.5000')
    
    def testMuuttujavirhe(self):
        assert    laske('tyhja_muuttuja*5') == 'S'

    def testSulkulauseke(self):
        assert    laske('2*(1+9)') == Decimal('20')

    def testSulut_sisakkain(self):
        assert    laske('10*((1+2)+(5*10))') == Decimal('530')

    def testSulut_vaarinpain(self):
        assert    laske('10*)(1+2)+(5*10))') == None

    def testSulut_vaaramaara(self):
        assert    laske('10*(1+2)+(5*10))') == None

    def testNollallajako(self):
        assert    laske('10/0') == None
        
    def testTyhjasyote(self):
        assert    laske('') == None
        
    def testEiaritmtetiikkaa(self):
        assert    laske('a+ b-c*d') == "S"
    
    def testkaksikertomerkkia(self): #(potenssi)
        assert    laske('5+2**5') == Decimal('37')
     
    def testkaksiplusmerkkia(self):
        assert    laske('5+2++5') == Decimal('12')
        
    def testkaksimiinusmerkkia(self): 
        assert    laske('5+2--5') == Decimal('12')
        
    def testplusmiinus(self): 
        assert    laske('5+2+-5') == Decimal('2')
      
    def testkertojako(self):
        assert    laske('5+2*/5') == None

    def testLaskettuNegatiivinenOperandi(self):
        assert    laske('3*(1-5)') == Decimal("-12")
    def testPitkadesimaali(self):
        assert not laske('-0.008333333333333333333333333333*0.0') == None
    def testPerusmuuttuja(self):
        assert laske('a', {'a': 1 } ) == Decimal("1")
    def testPerusFunktio(self):
        assert laske('log(a)', {'a': Decimal("100") } ) == Decimal("2")
    def testMinimiFunktio(self):
        assert laske('min(a)', {'a': Decimal("4") } ) == Decimal("4")
    def testListaFunktio(self):
        assert laske('min([a,3,1])', {'a': Decimal("100") } ) == Decimal("1")
    def testAbsMiinusparametri(self):
        assert laske('abs(-1)' ) == Decimal("1")
    
    def testSulkuMiinus(self):
        assert laske('(2)-1' ) == Decimal("1")

def haeTulos(tuloksetSarjalle, vartio, tehtava) :
                #Mukana olevat
                sarjanTulokset=tuloksetSarjalle[0]
                for vart_nro in range(1,len(sarjanTulokset)) :
                        va=None
                        for teht_nro in range(2,len(sarjanTulokset[vart_nro])):
                                tul =sarjanTulokset[vart_nro][teht_nro]
                                va= sarjanTulokset[vart_nro][0]
                                if va ==vartio and sarjanTulokset[0][teht_nro] ==tehtava:
                                        return tul
                #Ulkopuoliset
                for vart_nro in range(0,len(tuloksetSarjalle[1])) :
                        va=None
                        for teht_nro in range(2,len(tuloksetSarjalle[1][vart_nro])):
                                tul =tuloksetSarjalle[1][vart_nro][teht_nro]
                                va= tuloksetSarjalle[1][vart_nro][0]
                                if va ==vartio and tuloksetSarjalle[0][0][teht_nro] ==tehtava:
                                        return tul

def ViewSanityCheck(fixture_name):
        """
        Luo testcasen tarkistamaan sen, ett‰ kaikki n‰kym‰t toimivat kaatumatta.
        fixture name = tietokantafixtuurin nimi jolle testi luodaan.
        palauttaa TestCase:n
        """
        class testi(TestCase) :
                fixtures = [fixture_name]
                def testTulokset(self):
                        """
                        Ajaa jokaisen n‰kym‰n testidatalla
                        Testi antaa virheen jos jokin n‰kuma kaatuu.
                        """
                        kisat=Kisa.objects.all()
                        sarjat=Sarja.objects.all()
                        tehtavat=Tehtava.objects.all()
                        virheet=[]
                        request =HttpRequest()
                        maaritaKisa(request)
                        korvaaKisa(request)
                        for k in kisat : # Kisakohtaiset n‰kym‰t
                                kisa_nimi=k.nimi
                                kisa(request,kisa_nimi=kisa_nimi)
                                maaritaKisa(request,kisa_nimi=kisa_nimi)
                                maaritaValitseTehtava(request,kisa_nimi=kisa_nimi)
                                maaritaVartiot(request,kisa_nimi=kisa_nimi)
                                testiTulos(request,kisa_nimi=kisa_nimi)
                                syotaKisa(request,kisa_nimi=kisa_nimi)
                                laskennanTilanne(request,kisa_nimi=kisa_nimi)
                                tulosta(request,kisa_nimi=kisa_nimi)
                                tallennaKisa(request, kisa_nimi=kisa_nimi)
                                poistaKisa(request, kisa_nimi=kisa_nimi)
                        for s in sarjat: # Sarjakohtaiset n‰kym‰t
                                sarja_id=s.id
                                kisa_nimi=s.kisa.nimi
                                maaritaTehtava(request,kisa_nimi=kisa_nimi,sarja_id=sarja_id)
                                kopioiTehtavia(request,kisa_nimi=kisa_nimi,sarja_id=sarja_id)
                                tulostaSarja(request,kisa_nimi=kisa_nimi, sarja_id=sarja_id)
                                sarjanTuloksetCSV(request, kisa_nimi=kisa_nimi, sarja_id=sarja_id) 
                                tulostaSarjaHTML(request, kisa_nimi=kisa_nimi, sarja_id=sarja_id)
                        for t in tehtavat: # teht‰v‰kohtaiset n‰kym‰t
                                tehtava_id=t.id
                                kisa_nimi=t.sarja.kisa.nimi
                                maaritaTehtava(request,kisa_nimi=kisa_nimi,tehtava_id=tehtava_id)
                                syotaTehtava(request,kisa_nimi=kisa_nimi,tehtava_id=tehtava_id)
        return testi

def TulosTestFactory(fixture_name):
        """
        Tekee tulostestin halutulle tietokanta fixtuurille.
        fixture_name = fixtuurin nimi jolle testi tehd‰‰n.
        palauttaa TestCase:n
        """
        class testi(TestCase) :
                fixtures = [fixture_name]
                def testTulokset(self):
                        """
                        Iteroi jokaisen sarjan ja tehtavan.
                        Laskee tulokset ja vertaa tuloksia maariteltyihin testituloksiin.
                        Tunnistaa laskennan kaatavia virheita.
                        Tunnistaa v‰‰rat tulokset.
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
                                        if vaadittava==None:
                                                vaadittava="None"
                                        if tulos==None:
                                                tulos="None"
                                        if not tulos == vaadittava or tulos=="None":
                                                ilmoitus= virheilmoitus
                                                ilmoitus=ilmoitus + "\nTehtava: " + t.tehtava.nimi
                                                ilmoitus=ilmoitus + "\nKaava: " + t.tehtava.kaava
                                                ilmoitus=ilmoitus + "\nOstatehtavien kaavat: " 
                                                for k in OsaTehtava.objects.filter(tehtava=t.tehtava):
                                                        ilmoitus=ilmoitus + "\n"+k.nimi +"="+ k.kaava + " "
                                                        ilmoitus=ilmoitus + "\n  Parametrit: " 
                                                        for p in Parametri.objects.filter(osa_tehtava=k):
                                                                ilmoitus=ilmoitus + "\n    "+p.nimi+"="+p.arvo+" "
                                                        ilmoitus=ilmoitus + "\nSyotteet: "
                                                        for s in Syote.objects.filter(maarite__osa_tehtava=k).filter(vartio=t.vartio):

                                                                ilmoitus=ilmoitus + s.maarite.nimi+"="+ s.arvo + " "
                                                ilmoitus=ilmoitus + "\nVartio: "  + t.vartio.nimi  
                                                ilmoitus=ilmoitus + "\nTulos: "   + str(tulos)+' != '+str(vaadittava)
                                                virheet.append(ilmoitus) 
                        virhe= str(len(virheet)) + " errors"
                        for v in virheet:
                                virhe=virhe + "\n--------------------------------\n" + v 
                        self.failUnless( len(virheet) == 0 , unicode(virhe).encode('ascii', 'replace'))
        return testi

testit=[aritmeettinen_laskin_test]

# haetaan kaikki xml fixtuurien nimet.
# haetaan kaikki post txt:t
test_fixtures=[]
for f in os.listdir(os.curdir+"/fixtures/tests/"):
        if not f.find(".xml") == -1:
                test_fixtures.append("fixtures/tests/"+f)

#ajetaan vain haluttu fixtuuri
# Nollataan fixturet
#test_fixtures=[]
#test_fixtures.append("fixtures/tests/tehtavan_nimi_funktio.xml")

def PostTestFactory(fixture_name):
        """
        Testi joka ajaa n‰kymi‰ ennalta m‰‰ritellyill‰ testdatoilla.
        """
        from xml.dom.minidom import parse
        class testi(TestCase) :
                fixtures = [fixture_name]
                def testPost(self):
                        doc= parse(fixture_name)
                        post_requests=doc.getElementsByTagName("post_request")
                        for p in post_requests:
                                osoite="/"
                                if p.hasAttribute("address"):
                                        osoite= p.getAttribute("address")
                                inputs = p.getElementsByTagName("input")
                                data=[]
                                for i in inputs:
                                        if i.hasAttribute("name"):
                                                param=[i.getAttribute("name"),None]
                                                if i.hasAttribute("value"):
                                                        param[1]=i.getAttribute("value")
                                                data.append(param)
                                c = Client()
                                posti=dict(data)
                                c.post(osoite,posti)
        return testi

class TasapisteTesti(TestCase) :
        """
        Testaa tasapisteiss‰ m‰‰r‰‰vien teht‰vien toimintaa.
        """
        fixtures = ["fixtures/tests/tasapisteet.xml"]
        def testJarjestys(self):
                sarja=Sarja.objects.get(nimi="tiukka")
                tulokset=sarja.laskeTulokset()
                assert tulokset[0][1][0].nro==1
                assert tulokset[0][2][0].nro==2
                assert tulokset[0][3][0].nro==3
                assert tulokset[0][4][0].nro==4
                assert tulokset[0][5][0].nro==5
                assert tulokset[0][6][0].nro==6

# Tasapisteiss‰ m‰‰r‰‰v‰t teht‰v‰t testi
testit.append( TasapisteTesti )

#luodaan Post testit tekstitiedostoista
for t in test_fixtures:
        testit.append( PostTestFactory(t) )

#luodaan tulostestit fixtuureista.
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

