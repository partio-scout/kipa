#coding: latin-1
from decimal import *
import re
import AritmeettinenLaskin
from logger import lokkeri
import math
import operator

def is_number(s):
    if not s:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False

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
        "suurin" : "self.suurin" ,
        "itseisarvo" : "self.itseisarvo" ,
        "log10" : "self.log10" ,
        "if" : "self.ifSentence",
        "aika" : "self.aika",
        "minmaxsuoritus" : "self.minmaxsuoritus" }
         
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
def vertaa(a,operaattori,b) :
        """
        Vertaa a ja b keskenään operaattorilla 
        palauttaa True tai False
        parametrit merkkijonoja
        """
        vertailu = "Decimal(a)" + operaattori + "Decimal(b)"
        if eval(vertailu) :
                return True
        return False


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
                Neljä parametriä: 
                          1. Interpoloitava syöte,
                          2.Nollat tuottavan tuloksen kerroin keskimmäisestä 
                          3.Keskimmäisen laskutapa (med/kesk/kiinteö)
                          4.Arvo jolla saa maksimipisteet (numero/p/pienin/s/suurin)
                          5.Maksimipisteet. 
                """
                p=param[0]
                k=param[1]
                tapa = param[2]
                if param[2]=="med" or param[2]=="kesk" :
                        tapa=param[2]+"("+p+")"
                pm=param[3]
                maxp=param[4]
                if pm =="s" or  pm =="suurin" :
                        pm="suurin("+p+")"
                elif pm == "p" or pm == "pienin" :
                        pm="pienin("+p+")"

                #min(0,(maxp/(pm-k*med(p)))*(p-k*med(p)))
                kaava="minmax(0,"+maxp+",("+maxp+"/("+pm+"-"+k+"*"+tapa+"))*("+p+"-"+k+"*"+tapa + "))"

                lokkeri.setMessage( kaava ).logMessage()
                return kaava

        def mediaani(self,param):
                """
                Yksi parametri: Tehtävän syötteiden nimi joista lasketaan mediaani.
                Palauttaa mediaanin. Mikäli syötteitä ei löydy lainkaan palauttaa None
                Mediaaniin ei oteta mukaan ulkopuolella olevien vartioiden syötteitä. 
                """
                mediaani = unicode(self.teht.mediaani(param[0]))
                return mediaani

        def keskiarvo(self,param):
                """
                Yksi parametri: Tehtävän syötteiden nimi joista lasketaan keskiarvo.
                Palauttaa Keskiarvon. Mikäli syötteitä ei löydy lainkaan palauttaa None
                Keskiarvoon ei oteta tehtävässä ulkopuolella olevien vartoiden syötteitä.
                """
                keskiarvo = unicode(self.teht.keskiarvo(param[0]))
                return keskiarvo

        def suurin(self,param):
                """
                Yksi parametri: Tehtävän syötteiden nimi joista haetaan suurin arvo.
                Palauttaa joukon suurimman. Mikäli syötteitä ei löydy ollenkaan, palauttaa None.
                Suurinta arvoa ei haeta tehtävässä ulkopuolella olevien vartioiden syötteistä.
                """
                arvo=unicode(self.teht.suurin(param[0]))
                return arvo

        def pienin(self,param):
                """
                Yksi parametri: Tehtävän syötteiden nimi joista haetaan pienin arvo.
                Palauttaa joukon pienimmän. mikäli syötteitä ei löydy ollenkaan, palauttaa None
                Pienintä arvoa ei määritetä tehtävässä ulkopuolella olevien vartioiden syötteistä.
                """
                arvo=unicode(self.teht.pienin(param[0]) )
                return arvo
        def log10(self,param) :
                """
                10 kantainen logaritmi.
                1 parametri : Syöte taikka lause josta logaritmi lasketaan.
                """
                parametri= self.laske( param[0] )
                return unicode( Decimal( parametri ).log10() )

        def ifSentence(self,param) :
                """
                If lause.
                Kaksi pakollista parametriä. 
                Enismmäinen on testilause joka sisältää joko "==","<",">","<=",">=" vertaajia
                Toinen on arvo joka sijoitetaan jos testilause on totta.
                Samassa lauseessa voi verrata useampia muuttujia tai samaa useaan kertaan.
                esim. 
                if(1<A<2,1)
                if(A<B>C,666)
                If lauseessa voi olla myös optionaalinen kolmas parametri, 
                joka sijoitetaan jos vertailulause on epätosi.
                """
                operaattorit = "==|<=|>=|<|>"
                vertailulause=param[0]
                print vertailulause
                totta = param[1]
                tarua = None
                if len(param)>= 3 :
                        tarua = param[2]
                haku = "(^[^=<>]*)(" + operaattorit + ")(.*?)(" + operaattorit + "|$)(.*)"
                operoitavaa = re.search(haku,vertailulause)
                while operoitavaa :
                        verrattava1 = self.laske( operoitavaa.group(1) )
                        vertaaja =  operoitavaa.group(2)
                        verrattava2 = self.laske( operoitavaa.group(3) )
                        if verrattava1 == None or verrattava2 == None :
                                return None
                        if not vertaa(verrattava1,vertaaja,verrattava2) :
                                if tarua :
                                        return tarua
                                else :
                                        return 0
                        vertailulause = operoitavaa.group(3)+operoitavaa.group(4)+operoitavaa.group(5)
                        operoitavaa = re.search(haku,vertailulause)
                return totta

        def itseisarvo(self,param) :
                """
                Muuttaa negatiiviset arvot positiiviseksi.
                -Yksi parametri
                """
                parametri = self.laske(param[0])
                return unicode( abs( Decimal( parametri ) ) )
        def aika(self,param) :
                """
                Luo kaavaan aika arvon muodosta hh:mm:ss
                """
                arvot = param[0].split(":")
                arvo = unicode( Decimal(arvot[0])*60*60 + Decimal(arvot[1])*60 + Decimal(arvot[2]) )
                return arvo

        def minmaxsuoritus(self,param):
                """
                interpoloi minimi ja maksimi suortusten välin suoraviivaisesti
                (syöte,minimisuoritus,maksimisuoritus,jaettavatpisteet)
                """
                s =self.laske( param[0])
                min= self.laske(param[1])
                max= self.laske(param[2])
                pisteet=self.laske(param[3])
                kaava="interpoloi("+s+",1,"+min+","+ max+","+pisteet +")"
                print kaava
                return kaava

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
                print funktionNimi +"("+ parametrit +")"
                print "tulos " + tulos
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
                                muokattu=unicode(parsittu[0]) + unicode(tulos) + unicode(parsittu[2])
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
                lokkeri.setMessage( kaava ).logMessage()
                return muokattu

        def laskePisteet(self,syotteet,tehtava):
                """
                Laskee tuloksen valitulle tehtävälle ja syötteille.
                Palauttaa tuloksen jos tulos oli laskettavissa.
                Muuten None.
                """
                self.syot=syotteet
                self.teht=tehtava
                
                # Tulkataan muuttujat
                muuttujat=[]
                lokkeri.setMessage( "Tehtava: " + tehtava.nimi ).logMessage()
                lokkeri.setMessage( u"Syotteet: " ).logMessage()
                for s in syotteet:
                        lokkeri.setMessage( "    " + s.maarite.nimi + ' = "'+ unicode(s.arvo) + '"' ).logMessage()
                        muuttuja=unicode(s.arvo)
                        muuttujat.append( (s.maarite.nimi , muuttuja ) )
                self.muuttujaKirja = dict(muuttujat)

                # Ratkaistaan OsaTehtävät sekä suoran summan kaava:
                osatehtavat = self.teht.osapistekaava_set.all()
                ssKaava = ""
                for osa in osatehtavat :
                        osaPiste= self.laske(osa.kaava)

                        if osaPiste :
                            if osaPiste == "h" :
                                muuttujat.append( (osa.nimi,"0") )
                            else :
                                muuttujat.append( (osa.nimi,osaPiste) )

                        ssKaava=ssKaava + osa.nimi + "+"
                self.muuttujaKirja = dict(muuttujat)
                ssKaava=ssKaava[:-1]
                # Lasketaan tulos
                tulos = None
                if self.teht.kaava == "ss":
                        tulos = self.laske(ssKaava) 
                else :
                        tulos = self.laske(self.teht.kaava) 

                lokkeri.setMessage( "Pisteet: " + unicode(tulos) ).logMessage()
                return tulos

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

                for v in vartiot :
                        # Lisätään ensimmäiseen sarakkeeseen vartio objekti,toiseen yhteispisteet
                        rivi=[v,None]
                        yhteensa=Decimal(0)
                        for t in tehtavat:
                                pisteet =None
                                # Haetaan vartion syötteet tehtävälle
                                maaritteet = t.syotemaarite_set.all()
                                syotteet = []
                                for m in maaritteet :
                                        maaritteenSyotteet = m.syote_set.filter(vartio=v)
                                        if maaritteenSyotteet :
                                                if len(maaritteenSyotteet)==1 :
                                                        syotteet.append( maaritteenSyotteet[0] )
                                        else :
                                                # Syöttämättä
                                                pisteet = u"S"    

                                lokkeri.setMessage(u"\nTehtava: " + t.nimi).logMessage()
                                lokkeri.setMessage(u"Vartio: " + v.nimi ).logMessage()
                                
                                # Keskeyttänyt
                                if v.keskeyttanyt and v.keskeyttanyt<= t.jarjestysnro:
                                        pisteet = u"K"

                                # Lasketaan tulos
                                if not pisteet :
                                        pisteet= self.laskePisteet( syotteet, t )
                                
                                # Pyöristys
                                if pisteet and not pisteet == "S" and not pisteet == "K" :
                                        pisteet= unicode(Decimal(pisteet).quantize(Decimal('0.1'), rounding=ROUND_UP))
                                #Tuomarineuvos ylimääritys
                                tuomarineuvostonTulos=v.tuomarineuvostulos_set.filter(tehtava=t)
                                if len( tuomarineuvostonTulos ) == 1:
                                        pisteet =  tuomarineuvostonTulos[0].pisteet

                                #Tuloksen lisäys taulukkoon
                                if is_number(pisteet) :
                                        yhteensa = yhteensa + Decimal(pisteet)
                                rivi.append( pisteet )
                        rivi[1] = yhteensa
                        if v.keskeyttanyt==None and v.ulkopuolella==None:
                                mukana.append(rivi)
                        else :
                                ulkona.append(rivi)

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
 
