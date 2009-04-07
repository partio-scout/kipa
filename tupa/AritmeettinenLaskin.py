# coding: latin-1
from decimal import *
import re
from logger import *

def operoi(alku,operaattori,loppu) :
    """
    Poimii desimaaliluvun alku stringin lopusta, sekä loppu stringin alusta, 
    Suorittaa niille valitun lasku operaation. 
    Palauttaa merkkijonon jossa numerot ja operaattori on korvattu kyseisen operaation tuloksella.
    """ 
    numeronHakuLopusta=r'^\-\d*\.\d*\Z|^\-\d*\Z|\d*\.\d*\Z|\d*\Z|\d*\Z'
    numeronHakuAlusta =r'^\-\d*\.\d*|^\-\d*|\A\d*\.\d*|\A\d*|\A\d*'
    numeroA = re.search( numeronHakuLopusta,alku).group(0)
    numeroB = re.search( numeronHakuAlusta,loppu).group(0)
    if operaattori=='/' and numeroB=='0' :
        return None
    if len(numeroA)==0 or len(numeroB)==0 :
        return None
    lauseke="str( Decimal('" + numeroA + "')" 
    lauseke=lauseke + operaattori 
    lauseke=lauseke +"Decimal('" + numeroB + "'))"
    tulos = eval(lauseke)
    print lauseke
    print tulos
    lauseke=  re.sub(numeronHakuLopusta,"", alku) + tulos 
    lauseke=lauseke + re.sub(numeronHakuAlusta,"", loppu)
    return lauseke    

def suorita(kaava) :
    """
    Suorittaa merkkijonon laskutoimituksen jossa ei ole sulkeita () 
    Laskee ensin kerto- sekä jakolaskun * /
    Sitten plus ja miinus. + -
    Operaattoreiden välissä voi olla vain lukuja (-)(0-9)(.)(0-9)
    Palauttaa tuloksen merkkijonona.
    """
    laskettu=kaava
    operaattorit=( ("*","/") , ("+","-")  )
    haut = (r"\*|/",r"\+|\-")
    for r in range(len(haut)) :
        for o in operaattorit[r]  :
            if laskettu==None :
                return None
            haku=re.search( haut[r] , laskettu[1:] )
            if haku:
                i=haku.start()+1
                if laskettu[i] == o :
                        laskettu= operoi(laskettu[:i], o, laskettu[i+1:])
    
    if laskettu :
        if re.search(r'\*|/|\+|\-',laskettu[1:]) :
            return suorita(laskettu)
        else  :
            return laskettu
    else:
        return None


def laskeRekursiivisesti(kaava) :
    """
    Laskee kaavan sulkujen kanssa rekursiivisesti.
    Suortittaa +-*/ toimitukset.
    Mikäli laskussa on virhe palautusarvo on None.
    """
    muokattu = kaava.replace(" ","")
    #if validioi(muokattu)==False :
    #    return None
    sulku=re.search( r"\(" , muokattu)
    if sulku :
        i=sulku.start()
    
        lokkeri.setMessage(muokattu[:i+1])
        lokkeri.push()
        ratkaistuSulku=laskeRekursiivisesti(muokattu[i+1:])
        if ratkaistuSulku :
            lokkeri.setMessage(ratkaistuSulku).logMessage()
            muokattu=muokattu[:i]+ratkaistuSulku
            lokkeri.pop()
        else : 
            lokkeri.pop()
            return None
    sulku=re.search( r"\)" , muokattu)
    if sulku :
        i=sulku.start()
        suoritettu=suorita(muokattu[:i])
        if suoritettu:
            muokattu=suoritettu + muokattu[i+1:]
    if not re.search( r"\)" , muokattu):
        if not re.search( r"\(", muokattu):
             muokattu=suorita(muokattu)
    return muokattu

def validioi(kaava) :
     """
     Tarkistaa kaavan laskettavuuden:
     -Tarkistaa että kaava sisältää vain sallittuja merkkejä
     -Myöhemmin myös että sulut ovat oikein ja että operaattoreiden välissä on luku.
     Palauttaa True/False
     """
     #Kaavassa pitää olla laskettavaa:
     if len(kaava)==0 :
         return False
     
     # Kaava saa sisältää vain sallittuja merkkejä
     muokattu= re.sub('\d*\.?\d*',"", kaava)
     muokattu= re.sub('\+|\-|\*|/|\(|\)| ',"", muokattu)
     if not len(muokattu)==0: 
         return False 

     # Aukeavia ja sulkeutuvia sulkeita pitää olla saman verran.
     if kaava.count('(') or kaava.count(')'):
         if not kaava.count("(")==kaava.count(")")   :
             return False
 
     # operaattorit ei saa olla peräkkäin. 
     for eka in ("+","-","*","/") :
         for toka in ("+","*","/","-") :
             if not kaava.find(eka+toka)==-1:
                 return False
     
     return True

def laske(kaava) :
    """
    Laskee kaavan sulkujen kanssa
    Suortittaa +-*/ toimitukset.
    Palauttaa tuloksen jos kaava on laskettavissa. 
    Muussa tapauksessa palautusarvo on None.
    """
    if validioi(kaava)==False :
        return None
    else : 
        return laskeRekursiivisesti(kaava)

