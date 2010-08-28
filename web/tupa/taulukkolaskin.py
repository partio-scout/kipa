# encoding: utf-8
# KiPa(KisaPalvelu), tuloslaskentajärjestelmä partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi
import re
from decimal import *
from funktiot import funktiot
from funktiot import MathDict
from funktiot import DictDecimal



def dictToMathDict(dictionary) :
        """
        Muuttaa tavallisen sanakirjan rekursiivisesti laskennalliseksi sanakirjaksi.
        """
        new=MathDict({})
        for k in dictionary.keys():
                if type(dictionary[k])==dict : new[k]= dictToMathDict(dictionary[k])
                else : new[k]=dictionary[k]
        return new

def laske(lauseke,m={'num':DictDecimal}):
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
        except : return None
        if type(tulos)== DictDecimal : return Decimal(tulos)
        return tulos

def laskeTaulukko(taulukko,muuttujat) :
        """
        Laskee taulukon alkiot jotka ovat laskettavissa, muuttujista loytyvilla muuttujilla seka funktioilla.
        """
        # Maaritetaan numeroluokka eli vakiona lasketaan desimaaliluvuilla:
        m = { "num" : DictDecimal }
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

