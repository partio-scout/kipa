from decimal import *

def listaksi(joukkio):
        """
        Muuttaa sanakirjan tai desimaalin listaksi jos syote on joukkio, muuten palauttaa muuttujan itsessaan.
        """
        if type(joukkio)==list:
                lista=[]
                for i in joukkio :
                        if type(i)==Decimal : lista.append(i)
                return lista
        elif type( joukkio )==Decimal:
                return [joukkio]
        elif type( joukkio )==unicode or type( joukkio )==str:
                return joukkio
        else:
                try:
                        lista=[]
                        for k in joukkio.keys() :
                                if type(joukkio[k])==Decimal :
                                        lista.append(joukkio[k])
                        return lista
                except : return None 

def mediaani(joukko):
        """
        Palauttaa mediaanin arvon joukon lukuarvoista:
        joukko voi olla sanakirja tai lista
        Mikali lukujoukon pituus on parillinen palauttaa kahden keskimmaisen luvun keskiarvon.
        """
        lista = listaksi(joukko)
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

def minimi(joukko,b=None):  
        """
        Palauttaa joukon pienimman lukuarvon.
        Joukko voi olla sanakirja tai lista.
        """
        tulos=None
        if b and not type(joukko)==list and not type(b)==unicode: 
                tulos=min([joukko,b])
        else :tulos= min(listaksi(joukko))
        return tulos
def maksimi(joukko,b=None) :
        """
        Palauttaa joukon suurimman lukuarvon.
        Joukko voi olla sanakirja tai lista.
        """
        if b and not type(joukko)==list and not type(b)==unicode : 
                return max([joukko,b])
        else : return max(listaksi(joukko))

def keskiarvo(joukko) :
        """
        Palauttaa joukon lukuarvojen keskiarvon.
        Joukko voi olla sanakirja tai lista.
        """
        lista = listaksi(joukko)
        if not len(lista): return None
        total=Decimal(0) 
        for x in lista :
                total=total+x
        avg = total/len(lista)
        return avg

def summa(joukko) :
        """
        Palauttaa joukon lukuarvojen summan.
        Joukko voi olla sanakirja tai lista.
        """
        lista=None
        if type(joukko)==list : lista = joukko
        else : lista = listaksi(joukko)
        s=Decimal(0) 
        for v in lista : 
                if v and not type(v)==unicode and not type(v)==str: s=s+v
        return s

def interpoloi(x,x1,y1,x2,y2=0):
        """
        Palauttaa pisteen (x,y) y koordinaatin pisteiden (x1,y1) (x2,y2) maarittamalta suoralta.
        """
        # y = (y1-y2)/(x1-x2)*(x-x2)
        try :
                X=Decimal(x)
                X1=Decimal(x1)
                Y1=Decimal(y1)
                X2=Decimal(x2)
                Y2=Decimal(y2)
                tulos=(Y1-Y2) / (X1-X2) * (X-X2)
                tulos=mediaani([Decimal(0),Decimal(y1),tulos])
        except InvalidOperation : return None
        return tulos

def itseisarvo(a) :
        """
        Palauttaa a itseisarvon kun a on luku.
        Palauttaa a:n lukujen itseisarvot kun a on sanakirja.
        """
        tulos=None
        if type(a)==Decimal : tulos= abs(a)
        elif type(a)==str or type(a)==unicode :  tulos= abs(Decimal(a))
        else: 
                tulos={}
                for k in a.keys() : tulos[k] = abs(a[k])
        return tulos

def aikavali(a,b):
        """
        Palauttaa b-a kun a<b
        Palauttaa b-a+vrk mikali a>b
        Ajan yksikko on [s]
        a & b voivat olla lukuja tai sanakirjoja.
        """
        tulos=None
        # kaksi desimalilukua:
        if type(a)==Decimal and type(b)==Decimal :
                tulos= b-a
                if tulos < Decimal("0"): tulos=tulos+Decimal("86400") # lisataan 24h sekuntteina
        # kaksi merkkijonoa:
        elif type(a)==str or type(b)==str or type(a)==unicode or type(b)==unicode:
                tulos= Decimal(b)-Decimal(a)
                if tulos < Decimal("0"): tulos=tulos+Decimal("86400") # lisataan 24h sekuntteina
        # kaksi sanakirjaa:
        else: 
                tulos=b-a
                for i in tulos.keys() :
                        if tulos[i]<Decimal("0"): tulos[i]=tulos[i]+Decimal("86400")
        return tulos

funktiot= { "interpoloi" : interpoloi ,
                "aikavali" : aikavali ,
                "abs" : itseisarvo,
                "pienin" : minimi,
                "min" : minimi,
                "suurin" : maksimi, 
                "max" : maksimi , 
                "sum" : summa , 
                "med" : mediaani ,
                "kesk" : keskiarvo }


