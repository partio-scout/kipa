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
        Desimaali luokka , johon on toteutettu operoiminen MathDict instansseilla.
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
        elif type( joukkio )==Decimal:
                return [DictDecimal(joukkio)]
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


def suorita1(funktio,a) :
        if not type(a)==MathDict : return funktio(a)
        else : 
                rValue=MathDict({})
                for k in a.keys() :
                        try: rValue[k]= funktio(a[k])
                        except KeyError: pass
                        except TypeError : pass
                return rValue


def suorita2(funktio,a,b) :
        """
        Suorittaa valittua funktiota tarpeen mukaan a&b tyypistä riippuen.
        Muodostaa suoritteista laskukirjan tai yksittäisen desimaaliluvun.
        """
        if not type(a)==MathDict and not type(b)==MathDict: 
                return funktio(a,b)
        else :
                rValue=MathDict({})        
                if type(a)==MathDict :
                        for ak in a.keys():
                                if type(b)==MathDict:
                                        try:
                                                rValue[ak]= funktio(a[ak],b[ak])
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

