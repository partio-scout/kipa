# encoding: utf-8
# KiPa(KisaPalvelu), tuloslaskentajärjestelmä partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi


from decimal import *

class MathDict(dict):
        """
        Sanakirja jonka alkioille voi tehda massoittain 
        laskutoimituksia toisten sanakirjan vastaavien alkioiden kesken.
        """
        def __add__(self,other): 
                sum = MathDict({})
                for k in self.keys() : 
                        try:
                                if type(other) != MathDict : sum[k]=self[k]+other
                                else: sum[k]=self[k]+other[k]
                        except TypeError : pass
                        except KeyError: pass
                return sum
        def __sub__(self,other):
                sub = MathDict({})
                for k in self.keys() : 
                        try:
                                if type(other) != MathDict : sub[k]=self[k]-other
                                else: sub[k]=self[k]-other[k]
                        except TypeError : pass
                        except KeyError: pass
                return sub
        def __mul__(self,other):
                mult = MathDict({})
                for k in self.keys() : 
                        try:
                                if type(other) != MathDict : mult[k]=self[k]*other
                                else: mult[k]=self[k]*other[k]
                        except KeyError: pass
                        except TypeError : pass
                return mult
        def __div__(self,other):
                div = MathDict({})
                for k in self.keys() : 
                        try:
                                if type(other) != MathDict : div[k]=self[k]/other
                                else: div[k]=self[k]/other[k]
                        except KeyError: pass
                        except TypeError : pass
                return div

class DictDecimal(Decimal) :
        """
        Desimaali luokan , johon on toteutettu operoiminen MathDict instansseilla.
        """
        def __add__(self,other):
                add=DictDecimal()
                if type(other) == MathDict :
                        add = MathDict(other)
                        for k in other.keys() : 
                                try:
                                        add[k]=self+other[k]
                                except KeyError: pass
                                except TypeError : pass
                else:  add = DictDecimal(Decimal(self) + other)
                return add

        def __sub__(self,other):
                sub = Decimal()
                if type(other) == MathDict :
                        sub = MathDict(other)
                        for k in other.keys() : 
                                try:
                                        sub[k]=self-other[k]
                                except KeyError: pass
                                except TypeError : pass
                else: sub = DictDecimal(Decimal(self) - other)
                return sub

        def __mul__(self,other):
                mul = DictDecimal()
                if type(other) == MathDict :
                        mul = MathDict(other)
                        for k in other.keys() : 
                                try:
                                        mul[k]=self*other[k]
                                except KeyError: pass
                                except TypeError : pass
                else: mul= DictDecimal(Decimal(self) * other )
                return mul

        def __div__(self,other):
                div = DictDecimal()
                if type(other) == MathDict :
                        div = MathDict(other)
                        for k in other.keys() : 
                                try:
                                        div[k]=self/other[k]
                                except KeyError: pass
                                except TypeError : pass
                else: div= DictDecimal(Decimal(self) / other)
                return div

def listaksi(joukkio):
        """
        Muuttaa sanakirjan tai desimaalin listaksi jos syote on joukkio, muuten palauttaa muuttujan itsessaan.
        """
        if type(joukkio)==list:
                lista=[]
                for i in joukkio :
                        if type(i)==DictDecimal : lista.append(i)
                return lista
        elif type( joukkio )==DictDecimal:
                return [joukkio]
        elif type( joukkio )==unicode or type( joukkio )==str:
                return joukkio
        else:
                try:
                        lista=[]
                        for k in joukkio.keys() :
                                if type(joukkio[k])==DictDecimal or type(joukkio[k])==Decimal :
                                        lista.append(DictDecimal(joukkio[k]))
                        return lista
                except : return None 

def suorita(funktio,a,b) :
        """
        Suorittaa valittua funktiota tarpeen mukaan a&b tyypistä riippuen.
        Muodostaa suoritteista laskukirjan tai yksittäisen desimaaliluvun.
        """

        if not type(a)==MathDict or not type(b)==MathDict: return funktio(a,b)
        else :
                rValue=MathDict({})        
                if type(a)==MathDict :
                        for ak in a.keys():
                                if type(b)==MathDict:
                                        for bk in b.keys() :
                                                try:
                                                        rValue[ak]= funktio(a[ak],b[bk])
                                                except KeyError: pass
                                                except TypeError : pass
                                else :
                                        try:
                                                rValue[ak]= funktio(a[ak],b)
                                        except KeyError: pass
                                        except TypeError : pass
                else :
                        for bk in b.keys() :
                                try:
                                        rValue[bk]= funktio(a,b[bk])
                                except KeyError: pass
                                except TypeError : pass
                return rValue


def mediaani(joukko):
        """
        Palauttaa mediaanin arvon joukon lukuarvoista:
        joukko voi olla sanakirja tai lista
        Mikali lukujoukon pituus on parillinen palauttaa kahden keskimmaisen luvun keskiarvon.
        """
        lista = listaksi(joukko)
        values = sorted(lista)
        if len(values) % 2 == 1:
                return DictDecimal(values[(len(values)+1)/2-1])
        else:
                lower = values[len(values)/2-1]
                upper = values[len(values)/2]
                if type(upper)==str or type(lower)==str: 
                        upper=DictDecimal(upper)
                        lower=DictDecimal(lower)
                        
                return (DictDecimal(lower + upper)) / 2  

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
        total=DictDecimal(0) 
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
        s=DictDecimal(0) 
        for v in lista : 
                if v and not type(v)==unicode and not type(v)==str: s=s+v
        return s

def interpoloi(x,x1,y1,x2,y2=0):
        """
        Palauttaa pisteen (x,y) y koordinaatin pisteiden (x1,y1) (x2,y2) maarittamalta suoralta.
        """
        # y = (y1-y2)/(x1-x2)*(x-x2)
        try :
                X=DictDecimal(x)
                X1=DictDecimal(x1)
                Y1=DictDecimal(y1)
                X2=DictDecimal(x2)
                Y2=DictDecimal(y2)
                tulos=(Y1-Y2) / (X1-X2) * (X-X2)
                tulos=mediaani([DictDecimal(0),DictDecimal(y1),tulos])
        except InvalidOperation : return None
        return tulos

def itseisarvo(a) :
        """
        Palauttaa a itseisarvon kun a on luku.
        Palauttaa a:n lukujen itseisarvot kun a on sanakirja.
        """
        tulos=None
        if type(a)==DictDecimal : tulos= abs(a)
        elif type(a)==str or type(a)==unicode :  tulos= abs(DictDecimal(a))
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
        if type(a)==DictDecimal and type(b)==DictDecimal :
                tulos= b-a
                if tulos < DictDecimal("0"): tulos=tulos+DictDecimal("86400") # lisataan 24h sekuntteina
        # kaksi merkkijonoa:
        elif type(a)==str or type(b)==str or type(a)==unicode or type(b)==unicode:
                tulos= DictDecimal(b)-DictDecimal(a)
                if tulos < DictDecimal("0"): tulos=tulos+DictDecimal("86400") # lisataan 24h sekuntteina
        # kaksi sanakirjaa:
        else: 
                tulos=b-a
                for i in tulos.keys() :
                        if tulos[i]<DictDecimal("0"): tulos[i]=tulos[i]+DictDecimal("86400")
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


