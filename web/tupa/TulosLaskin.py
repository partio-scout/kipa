#coding: latin-1
from decimal import *
import re
import AritmeettinenLaskin
from logger import lokkeri

def haeSulku(lause):
    """
    Hakee lauseesta ensimmäisten sulkujen välissä olevan merkkijonon.
    Jos sulkuja ei löydy palauttaa None
    """
    auki=lause.find('(')
    index=0
    auenneita=0 
    if auki>=0:
       index=auki 
       auenneita=1
    auki_i=index
    while auenneita > 0 :
       kiini=lause[index:].find(')')
       auki=lause[index+1:].find('(')
       if kiini>=0 :
           if auki>=0:
               if kiini<auki :
                    index=index+kiini+1
                    auenneita=auenneita-1
               else:
                    index=index+auki+1
                    auenneita=auenneita+1
           else:
                index=index+kiini+1
                auenneita=auenneita-1
       else:
           assert 0
    
    if not auki_i==index:
        return (auki_i,index)
    else: 
        return None

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
        return merkkijono

class TulosLaskin :
    """
    Luokka jonka objektit laskevat tulospalvelun tulokset yhdelle vartiolle yhteen tehtävään
    """
    def max(self,param) :
        """
        Kasksi parametriä, maksimiarvo ja arvo. Molemmat voivat olla lausekkeita. 
        Palauttaa arvon mikäli se on maksimiarvoa pienempi. Muussa tapauksessa maksimiarvon, 
        tai None jos lausekkeet eivät ole laskettavissa. 
        """
        lokkeri.setMessage( param[0] + "," )
        lokkeri.push()
        arvo=self.laske(param[1],self.muuttujaKirja,self.funktioKirja)
        suurin=self.laske(param[0],self.muuttujaKirja,self.funktioKirja)
        lokkeri.pop()
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

        lokkeri.setMessage( param[0] + "," )
        lokkeri.push()
        arvo=self.laske(param[1],self.muuttujaKirja,self.funktioKirja)
        pienin=self.laske(param[0],self.muuttujaKirja,self.funktioKirja)
        lokkeri.pop()        

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
        return "min("+param[0]+",max("+param[1]+","+param[2]+"))"

    def interpoloi(self,param):
        """
        Neljä parametriä: Interpoloitava syöte, kerroin, keskimmäisen laskutapa , maksimipisteet, sekä arvo jolla saa suurimmat pisteet.
        Keskimmäisen laskutapa on joko "med"=mediaani tai "kesk"=keskimääräinen
        Arvo jolla saa parhaat pisteet voi olla myös "s" tai "p" Jolloin haetaan syöte joukon suurin tai pienin.
        """
        p=param[0]
        k=param[1]
        tapa="med"
        maxp=param[3]
        pm=param[4]
        if pm =="s":
           pm="suurin("+p+")"
        elif pm == "p":
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
        mediaani = str(self.teht.mediaani(param))
        return mediaani
    def keskiarvo(self,param):
        """
        Yksi parametri: Tehtävän syötteiden nimi joista lasketaan keskiarvo.
        Palauttaa Keskiarvon. Mikäli syötteitä ei löydy lainkaan palauttaa None
        Keskiarvoon ei oteta tehtävässä ulkopuolella olevien vartoiden syötteitä.
        """
        keskiarvo = str(self.teht.keskiarvo(param))
        return keskiarvo

    def suurin(self,param):
        """
        Yksi parametri: Tehtävän syötteiden nimi joista haetaan suurin arvo.
        Palauttaa joukon suurimman. Mikäli syötteitä ei löydy ollenkaan, palauttaa None.
        Suurinta arvoa ei haeta tehtävässä ulkopuolella olevien vartioiden syötteistä.
        """
        arvo=str(self.teht.suurin(param))
        return arvo

    def pienin(self,param):
        """
        Yksi parametri: Tehtävän syötteiden nimi joista haetaan pienin arvo.
        Palauttaa joukon pienimmän. mikäli syötteitä ei löydy ollenkaan, palauttaa None
        Pienintä arvoa ei haeta tehtävässä ulkopuolella olevien vartioiden syötteistä.
        """
        arvo=str(self.teht.pienin(param) )
        return arvo

    def laske(self,kaava,muuttujaKirja=None,funktioKirja=None) :
        """
        Laskee lausekkeen jossa on funktioita, muuttujia, sulkuja */ laskuja sekä +- laskuja.
        -Suorittaa ensin funktiot joiden nimet löytyvät funktioKirjasta.
        -Sijoittaa muuttujat, joille löytyy arvo muuttujaKirjasta.
        -Laskee sulkujen mukaan */ ensin sitten +-.
        -Mikäli lauseke oli laskettavissa palauttaa tuloksen. Muussa tapauksessa None.
        """
        self.muuttujaKirja=muuttujaKirja
        self.funktioKirja=funktioKirja
        muokattu=kaava

        haku= ""
        
        if funktioKirja:
            for i, j in funktioKirja.iteritems():  
                haku=haku+i+r"\("+r"|"
        haku=haku[:-1]
        kohdassa=re.search(haku, muokattu )

        while kohdassa  :
              sulut=haeSulku( muokattu[kohdassa.end()-1:])
              alku=muokattu[:kohdassa.start()]
              runko=funktioKirja[kohdassa.group(0)[:-1]]+"(pilkoParametreiksi('"+  muokattu[ sulut[0]+kohdassa.end() :sulut[1]+kohdassa.end()-2]+ "'))"
              
              lokkeri.setMessage( alku + kohdassa.group(0) )
              lokkeri.push()
              funktio= str(eval(runko)) 
              lokkeri.pop()
              loppu= muokattu[kohdassa.end()-1+sulut[1]:]
              muokattu=alku+funktio+loppu
              kohdassa=re.search(haku, muokattu )
              lokkeri.setMessage( muokattu ).logMessage()
        
        if muuttujaKirja:
            for i, j in muuttujaKirja.iteritems():  
                muokattu = muokattu.replace(i, j)  
            lokkeri.setMessage( muokattu ).logMessage()

        tulos= AritmeettinenLaskin.laske(muokattu)
        return tulos

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
           lokkeri.setMessage( "    " + s.maarite.nimi + " = "+ str(s.arvo) ).logMessage()
           muuttujat.append( (s.maarite.nimi , str(s.arvo) ) )
        # Lasketaan tulokset
        lokkeri.setMessage( "" )
        tulos = self.laske(self.teht.kaava, dict(muuttujat), { "interpoloi" : "self.interpoloi" ,"minmax" : "self.minmax" ,"max" : "self.max", "min" : "self.min" , "med" : "self.mediaani","kesk" : "self.keskiarvo" , "pienin" : "self.pienin" , "suurin" : "self.suurin" } ) 
        lokkeri.setMessage( "Pisteet: " + str(tulos) ).logMessage()
        return tulos

    def laskeSarja(self,sarja):
        """
        Laskee tulokset halutulle sarjalle. 
        Palauttaa kaksiuloitteisen taulukon[vartio][tehtävä] = pisteet.
        Taulukon ensimmäisissä sarakkeissa on vartio tai tehtävä objekteja muissa pisteitä.
        """
        tulokset=[[sarja]]
        rastit = sarja.rasti_set.all()
        tehtavat=[]
        for r in rastit :
             for t in r.tehtava_set.all():
                  tehtavat.append( t )
                  tulokset[0].append(t)
        vartiot = sarja.vartio_set.all()
        for v in vartiot :
            rivi=[v]
            for t in tehtavat: 
                maaritteet = t.syotemaarite_set.all()
                syotteet = []
                for m in maaritteet :
                     for s in m.syote_set.filter(vartio=v):
                          syotteet.append( s )

                lokkeri.setMessage("\nTehtävä: " + t.nimi).logMessage()
                lokkeri.setMessage("Vartio: " + v.nimi).logMessage()
                
                pisteet= self.laskePisteet( syotteet, t )
                #Tuomarineuvos ylimääritys
                tuomarineuvostonTulos=v.tuomarineuvostulos_set.filter(tehtava=t)
                if len( tuomarineuvostonTulos ) == 1:
                   pisteet =  tuomarineuvostonTulos[0].pisteet
                #Tuloksen lisäys
                rivi.append( pisteet )
            tulokset.append(rivi)
        return tulokset

