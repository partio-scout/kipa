# coding: latin-1
from decimal import *
import re

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
    
    if re.search(r'\*|/|\+|\-',laskettu[1:]) :
        return suorita(laskettu)   
    else:
        return laskettu

def validioi(kaava) :
     """
     Tarkistaa kaavan laskettavuuden:
     -Tarkistaa että kaava sisältää vain sallittuja merkkejä
     -Myöhemmin myös että sulut ovat oikein ja että operaattoreiden välissä on luku.
     Palauttaa True/False
     """
     if len(kaava)==0 :
         return False
     muokattu= re.sub('\d*\.?\d*',"", kaava)
     muokattu= re.sub('\+|\-|\*|/|\(|\)| ',"", muokattu)
     if len(muokattu)==0: 
         return True
     else :
         return False 

def laske(kaava,sanakirja=None) :
    """
    Laskee kaavan sulkujen kanssa rekursiivisesti.
    Suortittaa +-*/ toimitukset.
    Palauttaa tuloksen jos kaava on laskettavissa. 
    Muussa tapauksessa palautusarvo on None.
    """
    muokattu = kaava.replace(" ","")
    if validioi(muokattu)==False :
        return None
    sulku=re.search( r"\(" , muokattu)
    if sulku :
        i=sulku.start()
        muokattu=muokattu[:i]+laske(muokattu[i+1:])
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

