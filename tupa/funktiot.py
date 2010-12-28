# encoding: utf-8
# KiPa(KisaPalvelu), tuloslaskentajärjestelmä partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi

"""
Tässä tiedostossa on määritelty kaikki funktiot joita voi käyttää laskennan kaavoissa.
"""

from laskentatyypit import *
from math import *

def mediaani(joukko, *sarja):
        """
        Palauttaa mediaanin arvon joukon lukuarvoista:
        joukko voi olla sanakirja tai lista
        Mikali lukujoukon pituus on parillinen palauttaa kahden keskimmaisen luvun keskiarvon.
        """
        lista = listaksi(joukko,*sarja)
        values = sorted(lista)
        if len(values) % 2 == 1:
                return DictDecimal(values[(len(values)+1)/2-1])
        else:
                lower = DictDecimal(values[len(values)/2-1])
                upper = DictDecimal(values[len(values)/2])
                return (DictDecimal(lower + upper)) / 2  

def keskiarvo(joukko, *sarja) :
        """
        Palauttaa joukon lukuarvojen keskiarvon.
        Joukko voi olla sanakirja tai lista.
        """
        lista = listaksi(joukko,*sarja)
        if not len(lista): return None
        total=DictDecimal(0) 
        for x in lista :
                total=total+x
        avg = total/len(lista)
        return avg

def summa(joukko,*sarja) :
        """
        Palauttaa joukon lukuarvojen summan.
        Joukko voi olla sanakirja tai lista.
        """
        lista=listaksi(joukko,*sarja)
        s=DictDecimal(0) 
        for v in lista : 
                if v and not type(v)==unicode and not type(v)==str: s=s+v
        return s

def minimi(joukko, *sarja):  
        minimii = min( listaksi(joukko,*sarja) )
        return minimii

def maksimi(joukko,*sarja) : 
        return max( listaksi(joukko,*sarja) )

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

def aikavali(a,b):
        tulos= b-a
        if tulos < DictDecimal("0"): tulos=tulos+DictDecimal("86400") # lisataan 24h sekuntteina
        return tulos

lattia = lambda a: a.quantize(Decimal('1.'), rounding=ROUND_FLOOR)
katto = lambda a: a.quantize(Decimal('1.'), rounding=ROUND_CEILING)

logaritmi10 = getcontext().log10
luonnollinen_logaritmi = getcontext().ln
exponentti = getcontext().exp
modulus = getcontext().remainder
potenssi = getcontext().power
neliojuuri = getcontext().sqrt

def __jos(ehto,a,b) : 
        if ehto : return a 
        else : return b
def jos(ehto,a,b): return suorita(__jos,ehto,a,b)

perusfunktiot={ "abs" : abs,
                "aikavali" : aikavali ,
                "floor" : lattia,
                "ceil" : katto,
                "sqrt" : neliojuuri ,
                "exp"  : exponentti,
                "mod" : modulus,
                "pow" : potenssi,
                "power" : potenssi,
                "log" : logaritmi10 ,
                "ln" : luonnollinen_logaritmi ,
                "floor" : lattia ,
                "if" : jos }

listafunktiot={"pienin" : minimi,
                "min" : minimi,
                "suurin" : maksimi, 
                "max" : maksimi , 
                "sum" : summa , 
                "med" : mediaani ,
                "kesk" : keskiarvo,
                "mean" : keskiarvo }

# kavoissa käytettävät funktiot, ja niiden käyttönimet:
#           käyttönimi : funktio 
funktiot= { "interpoloi" : interpoloi }

