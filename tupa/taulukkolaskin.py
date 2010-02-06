# encoding: utf-8
# KiPa(KisaPalvelu), tuloslaskentajärjestelmä partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi


import re
from decimal import *
from funktiot import funktiot

class MathDict(dict):
        """
        Sanakirja jonka alkioille voi tehda massoittain 
        laskutoimituksia toisten sanakirjan vastaavien alkioiden kesken.
        """
        def __add__(self,other): 
                sum = MathDict({})
                for k in self.keys() : 
                        try:
                                if type(other) == Decimal : sum[k]=self[k]+other
                                else: sum[k]=self[k]+other[k]
                        except TypeError : pass
                        except KeyError: pass
                return sum
        def __sub__(self,other):
                sub = MathDict({})
                for k in self.keys() : 
                        try:
                                if type(other) == Decimal : sub[k]=self[k]-other
                                else: sub[k]=self[k]-other[k]
                        except TypeError : pass
                        except KeyError: pass
                return sub
        def __mul__(self,other):
                mult = MathDict({})
                for k in self.keys() : 
                        try:
                                if type(other) == Decimal : mult[k]=self[k]*other
                                else: mult[k]=self[k]*other[k]
                        except KeyError: pass
                        except TypeError : pass
                return mult
        def __div__(self,other):
                div = MathDict({})
                for k in self.keys() : 
                        try:
                                div[k]=self[k]/other[k]
                        except KeyError: pass
                        except TypeError : pass
                return div

def dictToMathDict(dictionary) :
        """
        Muuttaa taballisen sanakirjan rekursiivisesti laskennalliseksi sanakirjaksi.
        """
        new=MathDict({})
        for k in dictionary.keys():
                if type(dictionary[k])==dict : new[k]= dictToMathDict(dictionary[k])
                else : new[k]=dictionary[k]
        return new

def laske(lauseke,m={'num':Decimal}):
        """
        Laskee lauseen mikali se on laskettavissa. Kayttaa muuttujista loytyvia arvoja, seka funktioita.
        """
        # Poistetaan valilyonnit:
        lause = re.sub(" ","",lauseke)
        # Poistetaan "-0" termit
        lause=re.sub(r"([-][0](?![0-9.]))",r"",lause) 
        # Korvataan numerot merkkijonosta laskettavilla objekteilla
        lause=re.sub(r"(\d+\.\d+|(?<=[^0-9.])\d+)",r"num('\g<1>')",lause)
        # Korvataan muuttujien nimet oikeilla muuttujilla:
        lause=re.sub(r"\.([a-zA-Z_]+)(?=\.)",r"['\g<1>']",lause) # .x. -> [x].
        lause=re.sub(r"(?<!\d)\.([a-zA-Z0-9_]+)",r"['\g<1>']",lause)       # .x  -> [x]
        lause=re.sub(r"([a-zA-Z_]+(?=[[]))",r"m['\g<1>']",lause) # x[  -> m[x][
        # Korvataan yksinaiset muuttujat (lahinna funktioita):
        lause=re.sub(r"([a-zA-Z_]+(?![a-zA-Z_]*?[[']))",r"m['\g<1>']",lause) # x -> m[x]
        
        tulos=None
        # lasketaan tulos:
        try: 
                tulos = eval(lause)
        # Poikkeukset laskuille joita ei pysty laskemaan. 
        # Pyrkii myos estamaan koko paska kaadu virheissa.
        except DivisionByZero : return None 
        except KeyError : return "S" # syottamattomia muuttujia
        except TypeError :  return None 
        except SyntaxError: return None
        except NameError : return None
        return tulos

def laskeTaulukko(taulukko,muuttujat) :
        """
        Laskee taulukon alkiot jotka ovat laskettavissa, muuttujista loytyvilla muuttujilla seka funktioilla.
        """
        # Maaritetaan numeroluokka eli vakiona lasketaan desimaaliluvuilla:
        m = { "num" : Decimal }
        m.update(funktiot)
        # Paivitetaan kayttajan muuttujilla:
        m.update(muuttujat)
        m=dictToMathDict(m)
        tulokset=[]
        for x in taulukko :
                rivi=[]
                for lause in x : 
                        tulos=laske(lause,m)
                        if type(tulos)==Decimal : rivi.append(Decimal(tulos).quantize(Decimal('0.1'),
                                                                        rounding=ROUND_HALF_UP )) 
                        else: rivi.append(tulos)
                tulokset.append(rivi)
        return tulokset



