# encoding: utf-8
# KiPa(KisaPalvelu), tuloslaskentajärjestelmä partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi

import re
from laskentatyypit import *
from decimal import *
from funktiot import perusfunktiot
from funktiot import listafunktiot

pfunktiot={}
lfunktiot={}

for k in perusfunktiot.keys() : 
        def pfunctionfactory( funktio ) : return lambda *a : suorita(funktio,*a)
        pfunktiot[k]= pfunctionfactory( perusfunktiot[k] )  
for k in listafunktiot.keys() : 
        def lfunctionfactory( funktio ) : return lambda *a : suorita_lista(funktio,*a)
        lfunktiot[k]= lfunctionfactory(listafunktiot[k] )

def dictToMathDict(dictionary) :
        """
        Muuttaa tavallisen sanakirjan rekursiivisesti laskennalliseksi sanakirjaksi.
        """
        new=MathDict({})
        for k in dictionary.keys():
                if type(dictionary[k])==dict : new[k]= dictToMathDict(dictionary[k])
                else : new[k]=dictionary[k]
        return new

def laske(lauseke,m={},funktiot={}):
        """
        Laskee lauseen mikäli se on laskettavissa. Käyttää muuttujista loytyvia arvoja, seka funktioita.
        """
        # Määritetään numeroluokka eli vakiona lasketaan desimaaliluvuilla:
        f = { "num" : DictDecimal }
        f.update(funktiot)
        f.update(pfunktiot)
        f.update(lfunktiot)
        f=dictToMathDict(f)

        # Poistetaan välilyonnit ja enterit:
        lause = lauseke.replace('\n','')
        lause = lause.replace('\r','')
        lause = lause.replace(' ','')
        # Poistetaan "-0" termit
        lause=re.sub(r"([-][0](?![0-9.]))",r"",lause) 
        # Korvataan funktiot
        # Vakionumerot numeroinstansseiksi:
        lause=re.sub(r"((?<![^-+*/(,[])-?\d+([.]\d+)?)",r"num('\g<1>')",lause)
        # Korvataan muuttujien nimet oikeilla muuttujilla:
        lause=re.sub(r"\.([a-zA-Z_]\w*)(?=\.)",r"['\g<1>']",lause) # .x. -> [x].
        lause=re.sub(r"(?<!\d)\.([a-zA-Z_0-9]+)",r"['\g<1>']",lause)       # .x  -> [x]
        lause=re.sub(r"([a-zA-Z_]\w*(?=[[]))",r"m['\g<1>']",lause) # x[  -> m[x][
        # Korvataan yksinäiset muuttujat (lähinnä funktioita):
        lause=re.sub(r"([a-zA-Z_]\w*(?![a-zA-Z_0-9.(]*?[[']))",r"m['\g<1>']",lause) # x -> m[x]
        lause=re.sub(r"([a-zA-Z_]\w*(?![a-zA-Z_0-9.]*?[[']))",r"f['\g<1>']",lause) # x( -> f[x](
        tulos=None
        # lasketaan tulos:
        try: 
                tulos = eval(lause)
        # Poikkeukset laskuille joita ei pysty laskemaan. 
        # Pyrkii estämaan ettei koko paska kaadu virheissä.
        except DivisionByZero : return None 
        except KeyError : return "S" # Syottämättomiä muuttujia
        except TypeError :  return None 
        except SyntaxError: return None
        except NameError : return None
        except : return None
        if type(tulos)==DictDecimal : return Decimal(tulos)
        if type(tulos)==Decimal : return tulos
        if type(tulos)==unicode : return tulos
        if type(tulos)==int : return tulos
        if type(tulos)==str : return tulos
        return "S"

def laskeTaulukko(taulukko,muuttujat) :
        """
        Laskee taulukon alkiot jotka ovat laskettavissa, muuttujista loytyvilla muuttujilla seka funktioilla.
        """
        # Päivitetään käyttajän muuttujilla:
        m=dictToMathDict(muuttujat)
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



