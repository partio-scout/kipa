#coding: latin-1
from decimal import *
import re
import peruslaskin

def haeSulku(lause):
    """
    Hakee lauseesta ensimmäisten sulkujen paikat.
    palauttaa tuple(aukeva,sulkeutuva)
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

class laskin :
    """
    Luokka jonka objektit laskevat tulospalvelun tulokset yhdelle vartiolle yhteen tehtävään
    """
    def max(self,max,lauseke) :
        """
        Kasksi parametriä, maksimiarvo ja arvo. Molemmat voivat olla lausekkeita. 
        Palauttaa arvon mikäli se on maksimiarvoa pienempi. Muussa tapauksessa maksimiarvon, 
        tai None jos lausekkeet eivät ole laskettavissa. 
        """
        arvo=self.laske(lauseke,self.muuttujaKirja,self.funktioKirja)
        suurin=self.laske(max,self.muuttujaKirja,self.funktioKirja)
        if arvo and suurin and Decimal(arvo) > Decimal(suurin) :
            return suurin
        elif arvo and suurin:
            return arvo
        else :
            return None
    
    def min(self,min,lauseke) :
        """
        Kaksi parametriä, minimiarvo ja arvo. Molemmat voivat olla lausekkeita.
        Palauttaa arvon mikäli se on minimiarvoa suurempi. Muussa tapauksessa minimiarvon,
        tai None jos lausekkeet eivät ole laskettavissa.
        """
        arvo=self.laske(lauseke,self.muuttujaKirja,self.funktioKirja)
        pienin=self.laske(min,self.muuttujaKirja,self.funktioKirja)
         
        if not arvo:
            return None
        elif Decimal(arvo) < Decimal(pienin) :
            return pienin
        else :
            return arvo
    def minmax(self,min,max,arvo):
        """
        Kolme parametriä: minimiarvo, maksimiarvo, ja arvo. Ne voivat olla lausekkeita.
        Palauttaa arvon rajattuna minimiarvon ja maksimiarvon väliin. 
        Jos lauseet eivät ole laskettavissa palauttaa None.
        """
        return "min("+min+",max("+max+","+arvo+"))"

    def interpoloi(self,s,k,maxp,pm):
        """
        Neljä parametriä: Interpoloitava syöte, kerroin, maksimipisteet sekä arvo jolla saa suurimmat pisteet.
        Palauttaa Interpolointi kaavan. None jos syötteitä ei ole tarpeeksi
        """
        #min(0,(maxp/(pm-k*med(s)))*(s-k*med(s)))
        kaava="min(0,("+maxp+"/("+pm+"-"+k+"*"+"med("+s+")))*("+s+"-"+k+"*med("+s+")))"
        return kaava

    def med(self,param):
        """
        Yksi parmetri: Tehtävän syöte joista lasketaan mediaani.
        Palauttaa mediaanin. Mikäli syötteitä ei löydy lainkaan palauttaa None
        """
        mediaani = str(self.teht.mediaani(param))
        return mediaani

    def suorita(self,funktio,parametrit):
        """
        Suorittaa valitun funktion suluissa määritellyillä merkkijono parametreillä. Parametrit erotellaan pilkulla. 
        Parametrin sisäisten sulkujen välisiä pilkkuja ei erotella parametreiksi, 
        vaan ne annetaan ajettavalle funktiolle muuttamattomina. 
        Palauttaa funktion palautusarvon. Jos funktiota ei löydy. Palauttaa None
        """
        lista=parametrit.split(',')
        return funktio(*lista)

    def laske(self,kaava,muuttujaKirja=None,funktioKirja=None) :
        """
        Laskee lausekkeen jossa on funktioita, muuttujia, sulkuja */ laskuja sekä +- laskuja.
        -Suorittaa ensin funktiot joiden nimet löytyvät funktioKirjasta.
        -Sijoittaa muuttujat, joille löytyy arvo muuttujaKirjasta.
        -Laskee sulkujen mukaan */ ensin sitten +-.
        -Mikäli lauseke oli laskettavissa palauttaa tuloksen. Muussa tapauksessa None.
        """
        # Muuttujakirjaa sekä funktiokirjaa tarvitaan muissakin fuktioissa.
        self.muuttujaKirja=muuttujaKirja
        self.funktioKirja=funktioKirja
        muokattu=kaava
        # Suoritetaan funktiot.
        if funktioKirja:
            for i, j in funktioKirja.iteritems():  
                kohdassa=re.search(i, muokattu )
                while kohdassa:
                    sulut=haeSulku( muokattu[kohdassa.end():])
                    alku=muokattu[:kohdassa.start()]
                    funktio= self.suorita(j,muokattu[sulut[0]+kohdassa.end() +1:sulut[1]+kohdassa.end()-1])  
                    loppu= muokattu[kohdassa.end()+sulut[1]:]
                    muokattu=alku+funktio+loppu
                    kohdassa=re.search(i,muokattu )
        # Tulkataan muuttujat.
        if muuttujaKirja:
            for i, j in muuttujaKirja.iteritems():  
                muokattu = muokattu.replace(i, j)  
        # Lasketaan tulos
        return peruslaskin.laske(muokattu)

    def laskeTulos(self,syotteet,tehtava) :
        """
        Laskee tuloksen valitulle tehtävälle ja syötteille.
        Palauttaa tuloksen jos tulos oli laskettavissa.
        Muuten None.
        """
        self.syot=syotteet
        self.teht=tehtava
        # Tulkataan muuttujat
        muuttujat=[]
        for s in syotteet:
           muuttujat.append( ("tmax" ,str(self.teht.maksimipisteet) ))
           muuttujat.append( (s.lyhenne , str(s.arvo) ) )
           #muuttujat.append( (s.nimi, str(s.arvo) ) )
        # Lasketaan tulokset
        return self.laske(self.teht.kaava, dict(muuttujat), { "minmax" : self.minmax ,"max" : self.max, "min" : self.min , "med" : self.med, "interpoloi" : self.interpoloi } ) 

