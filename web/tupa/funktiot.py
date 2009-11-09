from decimal import *

def listaksi(sanakirja):
        """
        Muuttaa sanakirjan tai desimaalin listaksi jos syote on sanakirja, muuten palauttaa muuttujan itsessaan.
        """
        if type(sanakirja)==list:
                return sanakirja
        elif type(sanakirja)==Decimal:
                return [sanakirja]
        elif type(sanakirja)==unicode or type(sanakirja)==str:
                return None
        else:
                if not len(sanakirja.keys()): return None
                lista=[]
                for k in sanakirja.keys() :
                        if type(sanakirja[k])==Decimal :
                                lista.append(sanakirja[k])
                return lista
def mediaani(arvot):
        if type(arvot)==list : lista = arvot
        else :lista = listaksi(arvot)
        values = sorted(lista)
        if len(values) % 2 == 1:
                return Decimal(values[(len(values)+1)/2-1])
        else:
                lower = values[len(values)/2-1]
                upper = values[len(values)/2]
                if type(upper)==str or type(lower)==str: 
                        upper=Decimal(upper)
                        lower=Decimal(lower)
                        
                return (Decimal(lower + upper)) / 2  

def minimi(arvot,b=None):  
        tulos=None
        if b and not type(arvot)==list : 
                tulos=min([arvot,b])
        else :tulos= min(listaksi(arvot))
        return tulos
def maksimi(arvot,b=None) :
        if b and not type(arvot)==list : 
                return max([arvot,b])
        return max(listaksi(arvot))

def keskiarvo(arvot) :
        lista = listaksi(arvot)
        if not len(lista): return None
        total=Decimal(0) 
        for x in lista :
                total=total+x
        avg = total/len(lista)
        return avg

def summa(arvot) :
        lista=None
        if type(arvot)==list : lista = arvot
        else :lista = listaksi(arvot)
        s=0 
        for v in lista : 
                if v and not type(v)==unicode and not type(v)==str: s=s+v
        return s

def interpoloi(a,aMax,maxP,aNolla):
                """
                Nelja parametria: 
                          1.a=Interpoloitava arvo,
                          2.aMax = arvo jolla saa maksimipisteet
                          3.maxP = Jaettavat maksimipisteet
                          4.aNolla = arvo jolla saa nollat
                """
                #print "a="+str(a)+",aMax="+str(aMax)+",maxP="+str(maxP)+",aNolla="+str(aNolla)
                #(maxP/(aMax-aNolla))*(a-aNolla)
                try :
                        laskenta=(Decimal(maxP)/(Decimal(aMax)-Decimal(aNolla)))*(Decimal(a)-Decimal(aNolla))
                        tulos=mediaani([Decimal(0),Decimal(maxP),laskenta])
                except InvalidOperation : return None
                return tulos

funktiot= { "interpoloi" : interpoloi ,
                "pienin" : minimi,
                "min" : minimi,
                "suurin" : maksimi, 
                "max" : maksimi , 
                "sum" : summa , 
                "med" : mediaani ,
                "kesk" : keskiarvo }


