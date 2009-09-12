#coding: latin-1
from decimal import *
import re
import AritmeettinenLaskin
from logger import lokkeri
import math
import operator
from django.core.exceptions import ObjectDoesNotExist
                 
def is_number(s):
        if not s : return False
        try: float(s)
        except ValueError: return False
        return True

"""
Sanakirja erikoisfunktioista joita voi kutsua kaavoissa,
Ensimmäisenä nimi jolla viitataan kaavassa , jälkimmäisenä todellisen funktion nimi
"""
erikoisFunktiot = { 
        "interpoloi" : "self.interpoloi" ,
        "minmax" : "self.minmax" ,
        "max" : "self.max", 
        "min" : "self.min" , 
        "med" : "self.mediaani",
        "kesk" : "self.keskiarvo" , 
        "pienin" : "self.pienin" , 
        "suurin" : "self.suurin" ,
        "itseisarvo" : "self.itseisarvo" , 
        }
def parsiSulku(lause) :
        """
        Parsii lauseesta ensimmäiset sulut joiden sisällä ei ole sulkuja.
        Palauttaa (lauseen alku,sulkujen sisäpuoli,lauseen loppu)
        esim. parsiSulku( "5/(2*(3+2))" )
        palauttaa ( "5/(2*" , "3+2" , ")" )
        Mikäli sulkua ei löydy palauttaa None.
        """
        haku = re.search("(.*?)(?:[(])([^()]*)(?:[)])(.*)"  ,lause)
        if haku :
             return (haku.group(1),haku.group(2),haku.group(3))
        else : return None
       
def stringDecimaaliksi(merkkijono) :
        """
        Muuntaa merkkijonon Decimal objektiksi.
        Palauttaa None mikäli merkkijono ei ole muunnettavissa.
        """
        
        if merkkijono and re.search(r'^\d*\Z|^\d*\.\d*\Z', merkkijono ) :
                return Decimal(merkkijono)
        else : 
                return None

def sijoitaMuuttujat(kaava,muuttujaKirja):
        """
        Korvaa kaavasta löytyvät muuttujaKirjan mukaiset muuttujat.
        Muuttujan molemmilla puolilla kaavassa tulee olla joko operaattori,",", sulku tai merkkijonon alku tahi loppu.
        Palauttaa sijoitetun kaavan.
        """
        muokattu=kaava
        muuttui=True
        while muuttui==True :
                alussa=muokattu
                for i, j in muuttujaKirja.iteritems():  
                        muokattu = re.sub("(?<=[-+/*(),])"+i+"(?=[-+/*(),])",j.strip(),muokattu)  
                        muokattu = re.sub("(?<=^)"+i+"(?=[-+/*(),])",j.strip(),muokattu)  
                        muokattu = re.sub("(?<=^)"+i+"(?=$)",j.strip(),muokattu)  
                        muokattu = re.sub("(?<=[-+/*(),])"+i+"(?=$)",j.strip(),muokattu)
                if alussa==muokattu : muuttui=False
        return muokattu

def pilkoParametreiksi(merkkijono):
        """
        Pilkkoo merkkijonon listaksi pilkkujen kohdalta.
        Jos merkkijonossa on sulkuja ei pilkkomista tehdä sulkeiden sisältä.
        """
        sulkuja=0
        katkaistavatKohdat=[]
        for i in range(len(merkkijono)):
                if merkkijono[i]=='(':
                        sulkuja=sulkuja+1
                elif merkkijono[i]==')':
                        sulkuja=sulkuja-1
                elif merkkijono[i]==',' and sulkuja == 0 :
                        katkaistavatKohdat.append(i)
     
        if len(katkaistavatKohdat):
                parametrit=[]
                edellinenKohta=0
                for k in katkaistavatKohdat:
                        parametrit.append( merkkijono[edellinenKohta : k ] )
                        edellinenKohta=k+1
                parametrit.append(merkkijono[edellinenKohta :])
                return parametrit
        else: 
                return [merkkijono]

class TulosLaskin :
        """
        Luokka jonka objektit laskevat tuloksia.
        """
        funktioKirja = erikoisFunktiot

        def max(self,param) :
                """
                Kasksi parametriä, maksimiarvo ja arvo. Molemmat voivat olla lausekkeita. 
                Palauttaa arvon mikäli se on maksimiarvoa pienempi. Muussa tapauksessa maksimiarvon, 
                tai None jos lausekkeet eivät ole laskettavissa. 
                """
                arvo=self.laske(param[1])
                suurin=param[0]
                if arvo and suurin and Decimal(arvo) > Decimal(suurin) :
                        return suurin
                elif arvo and suurin:
                        return arvo
                else :
                        return None
    
        def min(self,param) :
                """
                Kaksi parametriä, minimiarvo ja arvo. Molemmat voivat olla lausekkeita.
                Palauttaa arvon mikäli se on minimiarvoa suurempi. Muussa tapauksessa minimiarvon,
                tai None jos lausekkeet eivät ole laskettavissa.
                """
                arvo=self.laske(param[1])
                pienin=param[0]
                if not arvo:
                        return None
                elif Decimal(arvo) < Decimal(pienin) :
                        return pienin
                else :
                        return arvo
        def minmax(self,param):
                """
                Kolme parametriä: minimiarvo, maksimiarvo, ja arvo. Ne voivat olla lausekkeita.
                Palauttaa arvon rajattuna minimiarvon ja maksimiarvon väliin. 
                Jos lauseet eivät ole laskettavissa palauttaa None.
                """
                a = param[0]
                b = param[1]
                c = param[2]
                lokkeri.setMessage( c ).logMessage()
                return "min("+a+",max("+b+","+c+"))"

        def interpoloi(self,param):
                """
                Neljä parametriä: 
                          1.a=Interpoloitava arvo,
                          2.aMax = arvo jolla saa maksimipisteet
                          3.maxP = Jaettavat maksimipisteet
                          4.aNolla = arvo jolla saa nollat
                """
                a=param[0]
                aMax=param[1]
                maxP = param[2]
                aNolla=param[3]
                
                #(maxP/(aMax-aNolla))*(a-aNolla)
                kaava="minmax(0,"+maxP+",("+maxP+"/("+aMax+"-"+aNolla+"))*("+a+"-"+aNolla+ "))"
                lokkeri.setMessage( kaava ).logMessage()
                return kaava

        def mediaani(self,param):
                """
                Yksi parametri: syote josta lasketaan mediaani.
                Palauttaa mediaanin. Mikäli syötteitä ei löydy lainkaan palauttaa None
                Mediaaniin ei oteta mukaan ulkopuolella olevien vartioiden syötteitä. 
                """
                if 'med_'+param[0] in self.optimoinnit:
                        # Optimointi: mediaani lasketaan vain kerran saman tehtävän sisällä
                        return self.optimoinnit['med_'+param[0]]
                syote=param[0]
                vartiot = self.teht.mukanaOlevatVartiot()
                tulokset=[]
                for v in vartiot:
                        maarite = self.osa_teht.syotemaarite_set.filter(nimi=syote)
                        if maarite:
                                try:
                                        vSyote=maarite[0].syote_set.get(vartio=v).arvo
                                        if vSyote:
                                                tulokset.append(Decimal(vSyote))
                                except ObjectDoesNotExist:
                                        pass
                def getMedian(numericValues):
                        if not len(numericValues):
                                return None
                        theValues = sorted(numericValues)
                        if len(theValues) % 2 == 1:
                                return theValues[(len(theValues)+1)/2-1]
                        else:
                                lower = theValues[len(theValues)/2-1]
                                upper = theValues[len(theValues)/2]
                        return (Decimal(lower + upper)) / 2  
                mediaani= str(getMedian(tulokset))
                self.optimoinnit['med_'+param[0]]=mediaani
                return mediaani

        def keskiarvo(self,param):
                """
                Yksi parametri: Kaava joista lasketaan keskiarvo.
                Palauttaa Keskiarvon. Mikäli syötteitä ei löydy lainkaan palauttaa None
                Keskiarvoon ei oteta tehtävässä ulkopuolella olevien vartoiden syötteitä.
                """
                assert 0

        def suurin(self,param):
                """
                Yksi parametri: Kaava jonka tuloksista haetaan suurin arvo.
                Palauttaa mukana olevista vartioista suurimman. Mikäli syötteitä ei löydy ollenkaan, palauttaa None.
                Suurinta arvoa ei lasketa tehtävässä ulkopuolella olevien vartioiden syötteistä.
                """
                if 'suurin_'+param[0] in self.optimoinnit:
                        # Optimointi: suurin haetaan vain kerran samassa tehtavassa
                        return self.optimoinnit['suurin_'+param[0]]

                syote=param[0]
                vartiot = self.teht.mukanaOlevatVartiot()
                tulokset=[]
                for v in vartiot:
                        maarite = self.osa_teht.syotemaarite_set.filter(nimi=syote)
                        if maarite:
                                vSyote=maarite[0].syote_set.get(vartio=v).arvo
                                if vSyote:
                                        tulokset.append(Decimal(vSyote))
                sarvo = str(max(tulokset))
                self.optimoinnit['suurin_'+param[0]]=sarvo
                return sarvo

        def pienin(self,param):
                """
                Yksi parametri: Tehtävän syötteiden nimi joista haetaan pienin arvo.
                Palauttaa mukana olevista vartioista pienimmän. mikäli syötteitä ei löydy ollenkaan, palauttaa None
                Pienintä arvoa ei lasketa tehtävässä ulkopuolella olevien vartioiden syötteistä.
                """
                if 'pienin_'+param[0] in self.optimoinnit:
                        # Optimointi: pienin haetaan vain kerran samassa tehtavassa
                        return self.optimoinnit['pienin_'+param[0]]
                syote=param[0]
                vartiot = self.teht.mukanaOlevatVartiot()
                tulokset=[]
                for v in vartiot:
                        maarite = self.osa_teht.syotemaarite_set.filter(nimi=syote)
                        if maarite:
                                try:
                                        vSyote=maarite[0].syote_set.get(vartio=v).arvo
                                        if vSyote:
                                                tulokset.append(Decimal(vSyote))
                                except ObjectDoesNotExist:
                                        pass
                parvo = str(min(tulokset))
                self.optimoinnit['pienin_'+param[0]]=parvo
                return parvo


        def itseisarvo(self,param) :
                """
                Muuttaa negatiiviset arvot positiiviseksi.
                -Yksi parametri
                """
                parametri = self.laske(param[0])
                return unicode( abs( Decimal( parametri ) ) )

        def suoritaFunktio(self,funktionNimi,parametrit) :
                """
                Suorittaa nimetyn erikoisfunktion
                Antaa funktiolle parametit merkkijonosta, jossa parametrit on eroteltu pilkulla.
                """
                listaParametreista= pilkoParametreiksi( parametrit )
                for p in listaParametreista :
                        if len(p.strip()) == 0 :
                                return None
                        p = self.laske(p)
                tulos = unicode(eval( erikoisFunktiot[funktionNimi] + "(listaParametreista)" ) )
                return tulos
        def sioitus(param):
                """
                Kertoo lausekkeen sioituksen lasketulla lausekkella. mitä pienempi tulos sen parempi.
                -1 parametri. syöte tai lauseke jonka pohjalta sijoitetaan.
                """
                return self.teht.sijoitus(param[0],)
                

        def haeFunktio(self , lause):
                """
                Hakee seuraavan funktiokirjasta löytyvän funktion lauseesta.
                palauttaa (funktiota edeltävä osa,funktion nimi)
                esim haeFunktio(5+5+5*Funktio(A)+4)
                palauttaa ("5+5+5*","Funktio")
                jos funktiota ei löydy palauttaa None
                """
                funktioHaku= "(\A|.*[-+*/(),])("
                if self.funktioKirja:
                        for i, j in self.funktioKirja.iteritems():  
                                funktioHaku=funktioHaku+i+"$"+"|"
                else :
                        funktioHaku=FunktioHaku+")"
                funktioHaku=funktioHaku[:-1]+")"
                funktio = re.search(funktioHaku, lause )
                if funktio :
                        return (funktio.group(1), funktio.group(2))
                else :
                        return None

        def ratkaiseSulku(self,lause) :
                """
                Ratkaisee ensimmäisen sulkuparin joka ei sisällä muita sulkuja.
                Jos sulut kuuluvat funktiolle, suoritetaan kyseinen funktio
                Muuten lasketaan sulkujen välinen lause Aritmeettisella laskimella.
                Palauttaa muokatun lauseen. 
                """
                muokattu = lause
                parsittu = parsiSulku(muokattu)
                if parsittu:
                        tulos=None
                        funktio=self.haeFunktio( parsittu[0] )
                        if funktio:
                                tulos = self.suoritaFunktio( funktio[1] , parsittu[1])
                                muokattu= funktio[0] + tulos + parsittu[2]
                        else:
                                laskettava=parsittu[1]
                                if self.muuttujaKirja:
                                        laskettava=sijoitaMuuttujat(laskettava,self.muuttujaKirja)
                                tulos = AritmeettinenLaskin.laske( laskettava )
                                muokattu=unicode(parsittu[0]) + unicode(tulos) + unicode(parsittu[2])
                return muokattu

        def laske(self,kaava):
                """
                Laskee lausekkeen jossa on funktioita, muuttujia, sulkuja, */ sekä +- laskuja.
                -Suorittaa funktioKirjasta löytyvät erikoisfunktiot.
                -Sijoittaa muuttujat, joille löytyy arvo muuttujaKirjasta.
                -Laskee sulkujen mukaan */ ensin sitten +-.
                -Mikäli lauseke oli laskettavissa palauttaa tuloksen. Muussa tapauksessa None.
                """
                muokattu=kaava.rstrip(
)
                # Suoritetaan sulkeet:
                sulkuja = muokattu.count("(") 
                while sulkuja:
                        muokattu = self.ratkaiseSulku(muokattu)
                        if muokattu :
                            sulkuja = muokattu.count("(") 
                        else :
                            sulkuja = 0
                # Lasketaan loppu :
                muokattu = sijoitaMuuttujat(muokattu,self.muuttujaKirja)
                muokattu = AritmeettinenLaskin.laske( muokattu)
                #lokkeri.setMessage( kaava ).logMessage()
                return muokattu

        def laskePisteet(self):
                """
                Laskee tuloksen valitulle tehtävälle ja syötteille.
                Palauttaa tuloksen jos tulos oli laskettavissa.
                Muuten None.
                """
                # Ratkaistaan OsaTehtävät sekä suoran summan kaava:
                osatehtavat = self.teht.osatehtava_set.all()
                ssKaava = ""
                muuttujat= []
                for osa in osatehtavat :
                        self.osa_teht=osa
                        osa_muuttujat=[]
                        
                        # Lisätään tehtävän parametri muuttujat.
                        for parametri in osa.parametri_set.all():
                                osa_muuttujat.append( (parametri.nimi,parametri.arvo) )
                        osa_kaava=sijoitaMuuttujat(osa.kaava,dict(osa_muuttujat))
                        
                        # Lisätään vartion syötteet.
                        for maarite in osa.syotemaarite_set.all():
                                for syote in maarite.syote_set.filter(vartio=self.vartio) :
                                        osa_muuttujat.append( (maarite.nimi,syote.arvo) )
                        
                        self.muuttujaKirja = dict(osa_muuttujat)
                        
                        if osa.kaava=="ss":
                                otk=""
                                for sm in osa.syotemaarite_set.all():
                                        otk=otk+sm.nimi+"+"
                                otk=otk[:-1]
                                osaPiste= self.laske(otk)
                                lokkeri.setMessage( "ot "+osa.nimi +" = " + otk ).logMessage()
                        else :
                                lokkeri.setMessage( "ot "+osa.nimi +" = " + osa_kaava ).logMessage()
                                osaPiste= self.laske(osa_kaava)
                                

                        if osaPiste :
                            if osaPiste == "h" :
                                muuttujat.append( (osa.nimi,"0") )
                            else :
                                muuttujat.append( (osa.nimi,osaPiste) )
                                muuttujat.append( (osa.nimi.upper(),osaPiste) )

                        ssKaava=ssKaava + osa.nimi + "+"
                self.muuttujaKirja = dict(muuttujat)
                ssKaava=ssKaava[:-1]
                # Lasketaan tulos
                tulos = None
                if self.teht.kaava == "ss":
                        lokkeri.setMessage( "teht kaava: " + ssKaava ).logMessage()
                        tulos = self.laske(ssKaava) 
                else :
                        lokkeri.setMessage( "teht kaava: " + self.teht.kaava ).logMessage()
                        tulos = self.laske(self.teht.kaava) 

                lokkeri.setMessage( "Pisteet: " + unicode(tulos) ).logMessage()
                return tulos

        def laskeVartio(self,vartio) :
                                v=vartio
                                t=self.teht
                                self.vartio=v
                                pisteet =None
                                # Haetaan vartion syötteet tehtävälle
                                
                                syotteet = []
                                
                                lokkeri.setMessage(u"\nTehtava: " + t.nimi).logMessage()
                                lokkeri.setMessage(u"Vartio: " + v.nimi ).logMessage()
                                
                                # Keskeyttänyt
                                if v.keskeyttanyt and v.keskeyttanyt<= t.jarjestysnro:
                                        pisteet = u"K"

                                # Lasketaan tulos
                                if not pisteet :
                                        pisteet= self.laskePisteet()
                                
                                # Pyöristys
                                if pisteet and not pisteet == "S" and not pisteet == "K" :
                                        pisteet= unicode(Decimal(pisteet).quantize(Decimal('0.1')))
                                #Tuomarineuvos ylimääritys
                                tuomarineuvostonTulos=v.tuomarineuvostulos_set.filter(tehtava=t)
                                if len( tuomarineuvostonTulos ) == 1:
                                        pisteet =  tuomarineuvostonTulos[0].pisteet

                                return pisteet

                                
        def laskeSarja(self,sarja):
                """
                Laskee tulokset halutulle sarjalle. 
                Palauttaa kaksiuloitteisen taulukon[vartio][tehtävä] = pisteet.
                Taulukon ensimmäisissä sarakkeissa on vartio tai tehtävä objekteja muissa pisteitä.
                Taulukon vasemmassa ylänurkassa on sarjan objekti
                """
                tehtavat = sarja.tehtava_set.all()
                vartiot = sarja.vartio_set.all()
                mukana = []
                ulkona = []

                # Luodaan tyhjä tulostaulukko
                for v in vartiot :
                        rivi=[v,Decimal("0")]
                        for t in tehtavat:
                                rivi.append( None)
                        if v.keskeyttanyt==None and v.ulkopuolella==None:
                                mukana.append(rivi)
                        else :
                                ulkona.append(rivi)
                
                for tindex in range(len(tehtavat)):
                        t= tehtavat[tindex]
                        self.teht=t
                        self.optimoinnit= {}
                        for vindex in range(len(mukana)):
                                pisteet = self.laskeVartio( mukana[vindex][0] )
                                #Tuloksen lisäys taulukkoon
                                if pisteet:
                                                try:
                                                        lisattava= Decimal(pisteet)
                                                        mukana[vindex][1] += lisattava
                                                except InvalidOperation:
                                                        pass
                                                mukana[vindex][tindex+2]=pisteet
                                
                        for vindex in range(len(ulkona)):
                                pisteet = self.laskeVartio( ulkona[vindex][0] )
                                #Tuloksen lisäys taulukkoon
                                if pisteet:
                                                try:
                                                        lisattava= Decimal(pisteet)
                                                        ulkona[vindex][1] += lisattava
                                                except InvalidOperation:
                                                        pass
                                                ulkona[vindex][tindex+2]=pisteet
                     
                mukana.sort( key=operator.itemgetter(1),reverse=True )
                ulkona.sort( key=operator.itemgetter(1),reverse=True )
                # Vasempaan ylänurkkaan sarjan objekti  
                tulosTaulu=[[sarja,"Yht."]]

                #Luodaan ensimmäinen rivi, jossa on tehtävä objektit
                for t in tehtavat:
                        tulosTaulu[0].append(t)
                for t in mukana:
                        tulosTaulu.append(t)
                tulosTaulu.append( ["Kisasta ulkopuolella:",] )
                for t in ulkona:
                        tulosTaulu.append(t)
                return tulosTaulu
 
