#coding: latin-1
from decimal import *
import re
import peruslaskin

def haeSulku(lause):
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
    def max(self,param) :
        arvo=self.laske(param[1],self.sanakirja,self.funktiokirja)
        suurin=self.laske(param[0],self.sanakirja,self.funktiokirja)
        if Decimal(arvo) > Decimal(suurin) :
            return suurin
        else :
            return arvo
    def min(self,param) :
        arvo=self.laske(param[1],self.sanakirja,self.funktiokirja)
        pienin=self.laske(param[0],self.sanakirja,self.funktiokirja)
         
        if not arvo:
            return None
        elif Decimal(arvo) < Decimal(pienin) :
            return pienin
        else :
            return arvo
    def minmax(self,param):
        return "min("+param[0]+",max("+param[1]+","+param[3]+"))"

    def interpoloi(self,param):
        p=param[0]
        k=param[1]
        maxp=param[2]
        pm=param[3]
        #min(0,(maxp/(pm-k*med(p)))*(p-k*med(p)))
        kaava="min(0,("+maxp+"/("+pm+"-"+k+"*"+"med("+p+")))*("+p+"-"+k+"*med("+p+")))"
        return kaava

    def med(self,param):
        mediaani = str(self.teht.mediaani(param[0]))
        return mediaani
    def laske(self,kaava,sanakirja=None,funktiokirja=None) :
        self.sanakirja=sanakirja
        self.funktiokirja=funktiokirja
        muokattu=kaava
        if funktiokirja:
            for i, j in funktiokirja.iteritems():  
                kohdassa=re.search(i, muokattu )
                while kohdassa:
                    sulut=haeSulku( muokattu[kohdassa.end():])
                    alku=muokattu[:kohdassa.start()]
                    runko=j+"('"+  muokattu[ sulut[0]+kohdassa.end() +1:sulut[1]+kohdassa.end()-1]+ "'.split(','))"
                    funktio= str(eval(runko)) 
                    loppu= muokattu[kohdassa.end()+sulut[1]:]
                    muokattu=alku+funktio+loppu
                    kohdassa=re.search(i,muokattu )
        if sanakirja:
            for i, j in sanakirja.iteritems():  
                muokattu = muokattu.replace(i, j)  
        return peruslaskin.laske(muokattu)

    def laskeTulos(self,syotteet,tehtava) :
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

