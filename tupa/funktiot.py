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

def minimi(joukko, *sarja):  return min( listaksi(joukko,*sarja) )
def maksimi(joukko,*sarja) : return max( listaksi(joukko,*sarja) )

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

def __aikavali(a,b):
        """
        Palauttaa b-a kun a<b
        Palauttaa b-a+vrk mikali a>b
        Ajan yksikko on [s]
        a & b voivat olla lukuja tai sanakirjoja.
        """
        tulos= b-a
        if tulos < DictDecimal("0"): tulos=tulos+DictDecimal("86400") # lisataan 24h sekuntteina
        return tulos

def aikavali(a,b) : return suorita(__aikavali,a,b)

def lattia(a) : return suorita(lambda a: a.quantize(Decimal('1.'), rounding=ROUND_FLOOR) ,a)
def katto(a) : return suorita(lambda a: a.quantize(Decimal('1.'), rounding=ROUND_CEILING) ,a)

itseisarvo  = lambda a : suorita(abs,a) 
logaritmi10 = lambda a :  suorita(getcontext().log10,a)
luonnollinen_logaritmi = lambda a :  suorita(getcontext().ln,a)
exponentti = lambda a :  suorita(getcontext().exp,a)
modulus = lambda a,b :  suorita(getcontext().remainder,a,b)
potenssi = lambda a,b :  suorita(getcontext().power,a,b)
neliojuuri = lambda a : suorita(getcontext().sqrt,a)

def __jos(ehto,a,b) : 
        if ehto : return a 
        else : return b
def jos(ehto,a,b): return suorita(__jos,ehto,a,b)

# kavoissa käytettävät funktiot, ja niiden käyttönimet:
#           käyttönimi : funktio 
funktiot= { "interpoloi" : interpoloi ,
                "aikavali" : aikavali ,
                "abs" : itseisarvo,
                "pienin" : minimi,
                "min" : minimi,
                "suurin" : maksimi, 
                "max" : maksimi , 
                "sum" : summa , 
                "med" : mediaani ,
                "kesk" : keskiarvo ,
                "log" : logaritmi10 ,
                "ln" : luonnollinen_logaritmi ,
                "floor" : lattia,
                "ceil" : katto,
                "sqrt" : neliojuuri ,
                "exp"  : exponentti,
                "mod" : modulus,
                "pow" : potenssi,
                "power" : potenssi,
                "if" : jos}


