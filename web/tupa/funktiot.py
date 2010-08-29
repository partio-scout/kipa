# encoding: utf-8
# KiPa(KisaPalvelu), tuloslaskentajärjestelmä partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi

"""
Tässä tiedostossa on määritelty kaikki funktiot joita voi käyttää laskennan kaavoissa.
"""

from laskentatyypit import *
from math import *

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
                lower = DictDecimal(values[len(values)/2-1])
                upper = DictDecimal(values[len(values)/2])
                return (DictDecimal(lower + upper)) / 2  

def minimi(joukko,b=None):  
        """
        Palauttaa joukon pienimman lukuarvon.
        Joukko voi olla sanakirja tai lista.
        """
        tulos=None
        if b and not type(joukko)==list and not type(b)==unicode: 
                tulos=min([joukko,b])
        else : tulos= min(listaksi(joukko))
        return tulos

def maksimi(joukko,b=None) :
        """
        Palauttaa joukon suurimman lukuarvon.
        Joukko voi o    lla sanakirja tai lista.
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
        return suorita1(abs,a) 

def __aikavali(a,b):
        """
        Palauttaa b-a kun a<b
        Palauttaa b-a+vrk mikali a>b
        Ajan yksikko on [s]
        a & b voivat olla lukuja tai sanakirjoja.
        """
        tulos=None
        # kaksi desimalilukua:
        tulos= b-a
        if tulos < DictDecimal("0"): tulos=tulos+DictDecimal("86400") # lisataan 24h sekuntteina
        return tulos
def aikavali(a,b) : return suorita2(__aikavali,a,b)

def __lattia(a) : return a.quantize(Decimal('1.'), rounding=ROUND_FLOOR) 
def lattia(a) : return suorita1(__lattia,a)
def __katto(a) : return a.quantize(Decimal('1.'), rounding=ROUND_CEILING) 
def katto(a) : return suorita1(__katto,a)

def logaritmi10(a) : 
        return suorita1(getcontext().log10,a)
def luonnollinen_logaritmi(a) : return suorita1(getcontext().ln,a)
def nelijojuuri(a) : return suorita1(getcontext().sqrt,a)
def exponentti(a) : return suorita1(getcontext().exp,a)
def modulus(a,b) : return suorita2(getcontext().remainder,a,b)
def potenssi(a,b) : return suorita2(getcontext().power,a,b)

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
                "sqrt" : nelijojuuri,
                "exp"  : exponentti,
                "mod" : modulus,
                "pow" : potenssi,
                "power" : potenssi }


