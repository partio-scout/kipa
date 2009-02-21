#coding: latin-1
from decimal import *
import re
import peruslaskin

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



class Laskin :
    """
    Luokka jonka objektit laskevat tulospalvelun tulokset yhdelle vartiolle yhteen tehtävään
    """
    def max(self,param) :
        """
        Kasksi parametriä, maksimiarvo ja arvo. Molemmat voivat olla lausekkeita. 
        Palauttaa arvon mikäli se on maksimiarvoa pienempi. Muussa tapauksessa maksimiarvon, 
        tai None jos lausekkeet eivät ole laskettavissa. 
        """
        arvo=self.laske(param[1],self.muuttujaKirja,self.funktioKirja)
        suurin=self.laske(param[0],self.muuttujaKirja,self.funktioKirja)
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
        arvo=self.laske(param[1],self.muuttujaKirja,self.funktioKirja)
        pienin=self.laske(param[0],self.muuttujaKirja,self.funktioKirja)
         
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
        return "min("+param[0]+",max("+param[1]+","+param[3]+"))"

    def interpoloi(self,param):
        """
        Neljä parametriä: Interpoloitava syöte, kerroin, maksimipisteet sekä arvo jolla saa suurimmat pisteet.
        Palauttaa Interpolointi kaavan. None jos syötteitä ei ole tarpeeksi
        """
        p=param[0]
        k=param[1]
        maxp=param[2]
        pm=param[3]
        #min(0,(maxp/(pm-k*med(p)))*(p-k*med(p)))
        kaava="min(0,("+maxp+"/("+pm+"-"+k+"*"+"med("+p+")))*("+p+"-"+k+"*med("+p+")))"
        return kaava

    def med(self,param):
        """
        Yksi parmetri: Tehtävän syöte joista lasketaan mediaani.
        Palauttaa mediaanin. Mikäli syötteitä ei löydy lainkaan palauttaa None
        """
        mediaani = str(self.teht.mediaani(param[0]))
        return mediaani

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
        if funktioKirja:
            for i, j in funktioKirja.iteritems():  
                kohdassa=re.search(i, muokattu )
                while kohdassa:
                    sulut=haeSulku( muokattu[kohdassa.end():])
                    alku=muokattu[:kohdassa.start()]
                    runko=j+"('"+  muokattu[ sulut[0]+kohdassa.end() +1:sulut[1]+kohdassa.end()-1]+ "'.split(','))"
                    funktio= str(eval(runko)) 
                    loppu= muokattu[kohdassa.end()+sulut[1]:]
                    muokattu=alku+funktio+loppu
                    kohdassa=re.search(i,muokattu )
        if muuttujaKirja:
            for i, j in muuttujaKirja.iteritems():  
                muokattu = muokattu.replace(i, j)  
        return peruslaskin.laske(muokattu)

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
        for s in syotteet:
           muuttujat.append( ("tmax" ,str(self.teht.maksimipisteet) ))
           muuttujat.append( (s.lyhenne , str(s.arvo) ) )
           #muuttujat.append( (s.nimi, str(s.arvo) ) )
        # Lasketaan tulokset
        return self.laske(self.teht.kaava, dict(muuttujat), { "minmax" : "self.minmax" ,"max" : "self.max", "min" : "self.min" , "med" : "self.med", "interpoloi" : "self.interpoloi" } ) 

    def laskeSarja(self,sarja):
        """
        Laskee tulokset halutulle sarjalle. 
        Palauttaa kaksiuloitteisen taulukon[vartio][tehtävä]=pisteet.
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
                rivi.append( self.laskePisteet( syotteet, t ) )
            tulokset.append(rivi)
        return tulokset

