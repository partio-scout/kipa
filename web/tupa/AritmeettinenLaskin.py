# coding: latin-1
from decimal import *
import re
from logger import lokkeri

def operoi(alku,operaattori,loppu) :
        """
        Poimii desimaaliluvun alku stringin lopusta, sekä loppu stringin alusta, 
        Suorittaa niille valitun lasku operaation. 
        Palauttaa merkkijonon jossa numerot ja operaattori on korvattu kyseisen operaation tuloksella.
        """ 
        numeronHakuLopusta = r'^\-\d*\.\d*\Z|^\-\d*\Z|\d*\.\d*\Z|\d*\Z|\d*\Z'
        numeronHakuAlusta =r'^\-\d*\.\d*|^\-\d*|\A\d*\.\d*|\A\d*|\A\d*'
        numeroA = re.search( numeronHakuLopusta,alku).group(0)
        numeroB = re.search( numeronHakuAlusta,loppu).group(0)
        
        if operaattori=='/' and numeroB=='0' :
                return None
        if not len(numeroA) or not len(numeroB) :
                return None
        lauseke=" Decimal('" + numeroA + "')" 
        lauseke=lauseke + operaattori 
        lauseke=lauseke +"Decimal('" + numeroB + "')"
        tulos = eval(lauseke)
        
        tulos = str(tulos)
        
        # Potenssimuotoisessa funktiossa pyöristetään
        if re.search( r"\dE[+-]\d",tulos ):
                tulos= str(Decimal(tulos).quantize(Decimal("1.0000")))

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

def parsiSulku(lause) :
        """
        Parsii lauseesta ensimmäiset sulut joiden sisällä ei ole sulkuja.
        Palauttaa (lauseen alku,sulkujen sisäpuoli,lauseen loppu)
        esim. parsiSulku( "5/(2*(3+2))" )
        palauttaa ( "5/(2*" , "3+2" , ")" )
        Mikäli sulkua ei löydy palauttaa None.
        """
        haku = re.search("(.*?)(?:[(])([^()]*)(?:[)])(.*)"  ,lause)
        if haku :
             return (haku.group(1),haku.group(2),haku.group(3))
        else :
             return None

def laskeSuluilla(kaava) :
        """
        Laskee kaavan sulkujen kanssa.
        Suortittaa +-*/ toimitukset.
        Mikäli laskussa on virhe palautusarvo on None.
        """
        muokattu=kaava
        sulkuja = muokattu.count("(") 
        for sulku in range(sulkuja) :
                parsittu = parsiSulku(muokattu)
                if parsittu :
                        muokattu= parsittu[0] + suorita(parsittu[1]) + parsittu[2]
        muokattu = suorita(muokattu)
        return muokattu
    
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


