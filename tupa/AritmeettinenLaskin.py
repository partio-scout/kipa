# coding: latin-1
from decimal import *
import re
from logger import lokkeri

def validioi(kaava) :
        """
        Tarkistaa kaavan laskettavuuden:
        -Tarkistaa että kaava sisältää vain sallittuja merkkejä
        -Myöhemmin myös että sulut ovat oikein ja että operaattoreiden välissä on luku.
        Palauttaa True/False
        """
        # Kaavassa pitää olla jotain:
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
        # Operaattorit ei saa olla peräkkäin, lukuunottamatta "-" jota käytetään negatiivisissa arvoissa. 
        for eka in ("+","-","*","/") :
                for toka in ("+","*","/") :
                        if not kaava.find(eka+toka)==-1:
                                return False
        return True

def laskeSuluilla(lauseke):
        """
        Laskee perus aritmeettisen lauseen pythonilla.
        """
        # numeroiden ympärille täytyy lisätä Decimal() määritteet.
        # näin laskenta tapahtuu 10 järjestelmän mukaan,
        # eikä heksadesimaaleina kuten esim floatilla. 
        muokattu=re.sub(r"((\d+\.)?\d+)",r"Decimal('\g<1>')",lauseke)
        tulos=None
        try:
                tulos = eval(muokattu)
                haku= re.search(r"\d+E[+-]\d+",str(tulos) ) 
                if haku :
                        tulos= tulos.quantize(Decimal('0.00001'))
        except DivisionByZero :
                return None
        return str(tulos)

def laske(kaava) :
        """
        Laskee lausekkeen sulkujen kanssa
        Suortittaa +-*/ toimitukset, sisimmät sulut ensimmäisenä.
        Palauttaa tuloksen jos lauseke on laskettavissa. 
        Muussa tapauksessa palautusarvo on None.
        """
        if validioi(kaava)==False :
                return None
        else : 
                stripattu = re.sub(" ","",kaava)
                return laskeSuluilla(stripattu)

