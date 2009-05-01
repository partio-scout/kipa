#coding: latin-1
from decimal import *
import re
import AritmeettinenLaskin
from logger import lokkeri

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
        "med" : "self.mediaani",
        "kesk" : "self.keskiarvo" , 
        "pienin" : "self.pienin" , 
        "suurin" : "self.suurin" }

def stringDecimaaliksi(merkkijono) :
        """
        Muuntaa merkkijonon Decimal objektiksi.
        Palauttaa None mikäli merkkijono ei ole muunnettavissa.
        """
        if re.search(r'^\d*\Z|^\d*\.\d*\Z', merkkijono ) :
                return Decimal(merkkijono)
        else : 
                return None

def sijoitaMuuttujat(kaava,muuttujaKirja):
        """
        Korvaa kaavasta löytyvät muuttujaKirjan mukaiset muuttujat.
        Muuttujan molemmilla puolilla kaavassa tulee olla joko operaattori, sulku tai merkkijonon alku tahi loppu.
        Palauttaa sijoitetun kaavan.
        """
        muokattu=kaava
        for i, j in muuttujaKirja.iteritems():  
                muokattu = re.sub("(?<=[-+/*()])"+i+"(?=[-+/*()])",j.strip(),muokattu)  
                muokattu = re.sub("(?<=^)"+i+"(?=[-+/*()])",j.strip(),muokattu)  
                muokattu = re.sub("(?<=^)"+i+"(?=$)",j.strip(),muokattu)  
                muokattu = re.sub("(?<=[-+/*()])"+i+"(?=$)",j.strip(),muokattu)
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
                return "min("+a+",max("+b+","+c+"))"

        def interpoloi(self,param):
                """
                Neljä parametriä: Interpoloitava syöte,
                          1.Nollat tuottavan tuloksen kerroin keskimmäisestä 
                          2.Keskimmäisen laskutapa (med/kesk)
                          3.Arvo jolla saa maksimipisteet (numero/p/pienin/s/suurin)
                          4.Maksimipisteet. 
                """
                p=param[0]
                k=param[1]
                tapa="med"
                pm=param[3]
                maxp=param[4]
                if pm =="s" or  pm =="suurin" :
                        pm="suurin("+p+")"
                elif pm == "p" or pm == "pienin" :
                        pm="pienin("+p+")"

                #min(0,(maxp/(pm-k*med(p)))*(p-k*med(p)))
                kaava="minmax(0,"+maxp+",("+maxp+"/("+pm+"-"+k+"*"+tapa+"("+p+")))*("+p+"-"+k+"*"+tapa+"("+p+")))"
                return kaava

        def mediaani(self,param):
                """
                Yksi parametri: Tehtävän syötteiden nimi joista lasketaan mediaani.
                Palauttaa mediaanin. Mikäli syötteitä ei löydy lainkaan palauttaa None
                Mediaaniin ei oteta mukaan ulkopuolella olevien vartioiden syötteitä. 
                """
                mediaani = str(self.teht.mediaani(param[0]))
                return mediaani

        def keskiarvo(self,param):
                """
                Yksi parametri: Tehtävän syötteiden nimi joista lasketaan keskiarvo.
                Palauttaa Keskiarvon. Mikäli syötteitä ei löydy lainkaan palauttaa None
                Keskiarvoon ei oteta tehtävässä ulkopuolella olevien vartoiden syötteitä.
                """
                keskiarvo = str(self.teht.keskiarvo(param[0]))
                return keskiarvo

        def suurin(self,param):
                """
                Yksi parametri: Tehtävän syötteiden nimi joista haetaan suurin arvo.
                Palauttaa joukon suurimman. Mikäli syötteitä ei löydy ollenkaan, palauttaa None.
                Suurinta arvoa ei haeta tehtävässä ulkopuolella olevien vartioiden syötteistä.
                """
                arvo=str(self.teht.suurin(param[0]))
                return arvo

        def pienin(self,param):
                """
                Yksi parametri: Tehtävän syötteiden nimi joista haetaan pienin arvo.
                Palauttaa joukon pienimmän. mikäli syötteitä ei löydy ollenkaan, palauttaa None
                Pienintä arvoa ei määritetä tehtävässä ulkopuolella olevien vartioiden syötteistä.
                """
                arvo=str(self.teht.pienin(param[0]) )
                return arvo
    
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
                tulos = str(eval( erikoisFunktiot[funktionNimi] + "(listaParametreista)" ) )
                return tulos
        
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
                parsittu = AritmeettinenLaskin.parsiSulku(muokattu)
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
                                muokattu=str(parsittu[0]) + str(tulos) + str(parsittu[2])
                                lokkeri.setMessage( muokattu ).logMessage()
                return muokattu

        def laske(self,kaava):
                """
                Laskee lausekkeen jossa on funktioita, muuttujia, sulkuja, */ sekä +- laskuja.
                -Suorittaa funktioKirjasta löytyvät erikoisfunktiot.
                -Sijoittaa muuttujat, joille löytyy arvo muuttujaKirjasta.
                -Laskee sulkujen mukaan */ ensin sitten +-.
                -Mikäli lauseke oli laskettavissa palauttaa tuloksen. Muussa tapauksessa None.
                """
                muokattu=kaava
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
                return muokattu

        def laskePisteet(self,syotteet,tehtava):
                """
                Laskee tuloksen valitulle tehtävälle ja syötteille.
                Palauttaa tuloksen jos tulos oli laskettavissa.
                Muuten None.
                """
                self.syot=syotteet
                self.teht=tehtava
                lokkeri.setMessage( "Kaava: " + str(self.teht.kaava) ).logMessage()
                
                # Tulkataan muuttujat
                muuttujat=[]
                for s in syotteet:
                        lokkeri.setMessage( "    " + s.maarite.nimi + ' = "'+ str(s.arvo) + '"' ).logMessage()
                        muuttuja=str(s.arvo)
                        muuttujat.append( (s.maarite.nimi , muuttuja ) )
                self.muuttujaKirja = dict(muuttujat)
                
                # Lasketaan tulos
                tulos = self.laske(self.teht.kaava) 
                lokkeri.setMessage( "Pisteet: " + str(tulos) ).logMessage()
                return tulos

        def laskeSarja(self,sarja):
                """
                Laskee tulokset halutulle sarjalle. 
                Palauttaa kaksiuloitteisen taulukon[vartio][tehtävä] = pisteet.
                Taulukon ensimmäisissä sarakkeissa on vartio tai tehtävä objekteja muissa pisteitä.
                Taulukon vasemmassa ylänurkassa on sarjan objekti
                """

                # Vasempaan ylänurkkaan sarjan objekti  
                tulokset=[[sarja]]

                #Luodaan ensimmäinen rivi, jossa on tehtävä objektit
                tehtavat=sarja.tehtava_set.all()
                for t in tehtavat:
                        tulokset[0].append(t)
                vartiot = sarja.vartio_set.all()
                
                for v in vartiot :
                        # Lisätään ensimmäiseen sarakkeeseen vartio objekti
                        rivi=[v]
                        for t in tehtavat:
                                # Haetaan vartion syötteet tehtävälle
                                maaritteet = t.syotemaarite_set.all()
                                syotteet = []
                                for m in maaritteet :
                                        for s in m.syote_set.filter(vartio=v):
                                                syotteet.append( s )

                                lokkeri.setMessage("\nTehtava: " + t.nimi).logMessage()
                                lokkeri.setMessage("Vartio: " + v.nimi).logMessage()
                                
                                # Lasketaan tulos
                                pisteet= self.laskePisteet( syotteet, t )
                                if pisteet:
                                        pisteet= str(Decimal(pisteet).quantize(Decimal('0.1'), rounding=ROUND_UP))

                                #Tuomarineuvos ylimääritys
                                tuomarineuvostonTulos=v.tuomarineuvostulos_set.filter(tehtava=t)
                                if len( tuomarineuvostonTulos ) == 1:
                                        pisteet =  tuomarineuvostonTulos[0].pisteet

                                #Tuloksen lisäys taulukkoon
                                rivi.append( pisteet )
                        tulokset.append(rivi)
                return tulokset
 
