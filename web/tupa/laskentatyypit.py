# encoding: utf-8
# KiPa(KisaPalvelu), tuloslaskentajärjestelmä partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi
from decimal import *

class SequenceOperations :
        def __add__(self,other): return self.operate_to_all( lambda a,b: a+b , other)
        def __sub__(self,other): return self.operate_to_all( lambda a,b: a-b , other)
        def __mul__(self,other): return self.operate_to_all( lambda a,b: a*b , other)
        def __div__(self,other): return self.operate_to_all( lambda a,b: a/b , other)
        def __lt__(self, other): return self.operate_to_all( lambda a,b: a<b , other)
        def __le__(self, other): return self.operate_to_all( lambda a,b: a<=b, other)
        def __eq__(self, other): return self.operate_to_all( lambda a,b: a==b, other)
        def __ne__(self, other): return self.operate_to_all( lambda a,b: a!=b, other)
        def __gt__(self, other): return self.operate_to_all( lambda a,b: a>b , other)
        def __ge__(self, other): return self.operate_to_all( lambda a,b: a>=b, other)

class MathDict(SequenceOperations,dict):
        """
        Sanakirja jonka alkioille voi tehda massoittain 
        laskutoimituksia toisten sanakirjan vastaavien alkioiden kesken.
        """
        # Utility function
        def operate_to_all(self,function2, other) :
                oper = MathDict({})
                for k in self.keys() : 
                        try:
                                if type(other) != MathDict : oper[k]=function2(self[k],other)
                                else: oper[k]=function2(self[k],other[k])
                        except KeyError: pass
                        except TypeError : pass
                return oper

class DictDecimal(SequenceOperations,Decimal) :
        """
        Desimaali luokka , johon on toteutettu operoiminen MathDict instansseilla.
        """
        def operate_to_all(self,function2,other ) :
                oper=DictDecimal()
                if type(other) == MathDict :
                        oper = MathDict(other)
                        for k in other.keys() : 
                                try:
                                        oper[k]=function2(self,other[k])
                                except KeyError: pass
                                except TypeError : pass
                else:  oper = DictDecimal( function2(Decimal(self), other) )
                return oper
        
def listaksi(a,*opt):
        """
        Muuttaa sanakirjan tai desimaalin listaksi jos syote on joukkio, muuten palauttaa muuttujan itsessaan.
        """
        if len(opt) : 
                joukkio = [a]
                joukkio += opt
        else : joukkio = a 

        if type(joukkio)==list:
                return joukkio
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

def run_dict(list,funktio,*param):
        mdict=None
        for p in param : 
                if type(p) == MathDict and not mdict : mdict=p
        if not mdict : return funktio(*param)
        rValue=MathDict({})
        for k in mdict.keys() :
                parametrit = []
                for p in param : 
                        if type(p)== MathDict : parametrit.append(p[k])
                        else : parametrit.append(p)
                try: 
                        if list: rValue[k]= listaksi(*parametrit)
                        else : rValue[k]= funktio(*parametrit)
                except KeyError: pass
                except TypeError : pass
        return rValue        

def suorita(funktio,*param):
        return run_dict(0,funktio,*param)

def suorita_lista(funktio,a,*param ) :
        if len(param)==0 : 
                return funktio( listaksi(a) )
        else : return run_dict(1,funktio,a,*param)

