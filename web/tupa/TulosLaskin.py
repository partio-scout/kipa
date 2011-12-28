# encoding: utf-8
# KiPa(KisaPalvelu), tuloslaskentajärjestelmä partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi


if not __name__ == "__main__":
	from logger import lokkeri
	from funktiot import *


from decimal import *
from laskentatyypit import *
import re
from taulukkolaskin import *
import math
import operator
#from django.core.exceptions import ObjectDoesNotExist

def korvaa(lause,pino,loppu=None) :
    """
    Korvaa lauseen muuttujat pinon mukaisella etuliitteella a.b.c jne.
    "." lausessa muuttujan edessa liikuttaa muuttujaa pinossa ylospain 
    optionaalinen loppu parametri lisaa muuttujan peraan arvon. 
    loppu parametri poistuu ensimmaisella .a operaatiola
    esim: 
    >>> korvaa("c",["a","b"])
    'a.b.c'
    >>> korvaa(".c",["a","b"])
    'a.c'
    >>> korvaa("5+..c",["a","b"])
    '5+c'
    >>> korvaa("c",["a","b"],"56")
    'a.b.c.56'
    >>> korvaa(".c",["a","b"],"56")
    'a.b.c'
    >>> korvaa("..c",["a","b"],"56")
    'a.c'
    >>> korvaa("5+...c",["a","b"],"56")
    '5+c'
    >>> korvaa("5+...c*c",["a","b"],"56")
    '5+c*a.b.c.56'
    >>> korvaa("c(c)",["a","b"])
    'c(a.b.c)'
    >>> korvaa("funktio(c)",["a","b"])
    'funktio(a.b.c)'
    >>> korvaa("a.b...a..56",["a","b"],"56")
    '56'
    >>> korvaa("eka.toka...eka..56",["eka","toka"],"56")
    '56'
    """
    # Ensiksi täytyy poistaa kaikki x..y -> y
    poistoon= re.search(r"([^-.+*/(),]+[.][.])",lause) 
    while poistoon :
        lause=re.sub(r"([^-.+*/()]+[.][.])","",lause,count=1)
        poistoon= re.search(r"([^-.+*/()]+[.][.])",lause) 
    haku= re.finditer("(\.{0,3})([a-zA-Z]\w*)(?:\.(\w+))?(?:\.(\w+))?(?:\.(\w+))?(?!\w*[(])",lause )
    muutokset=[]
    for h in haku :
                ryhmat= h.groups()
                vanha=ryhmat[0]
                uusi=""
                paluu=len(ryhmat[0])
                if loppu:
                        if paluu>0 : paluu=paluu-1
                kohtaan = len(pino)-paluu
                for i in range(kohtaan) :
                        uusi=uusi+"." +pino[i]
                for g in ryhmat[1:] :
                        if g: 
                                uusi=uusi+"."+g
                                vanha=vanha+"."+g
                vanha=vanha[1:]
                if loppu and len(ryhmat[0])==0: 
                        uusi=uusi+"."+loppu
                uusi=uusi[1:]
                muutokset.append((h.start(),h.end(),uusi))
    if not len(muutokset) : return lause
    muokattu=lause[:muutokset[0][0]]
    for i in range(len(muutokset)-1):
                muokattu=muokattu+muutokset[i][2]
                muokattu=muokattu+lause[muutokset[i][1]:muutokset[i+1][0]]
    muokattu=muokattu+muutokset[-1][2]
    muokattu=muokattu+lause[muutokset[-1][1]:]
    return muokattu

def suoritusJoukko(s) :
    """  Siirtää parametriä yhden pykälän yleisempään suuntaaan.
    Jolloin esim. vartion suorituksesta a tulee .a Joka on kaikkien saman sarjan vartioiden vastaava suoritus.
    >>> suoritusJoukko('a')
    '.a'
    >>> suoritusJoukko('a*b+c')
    '.a*.b+.c'
    >>> suoritusJoukko('aikavali(...eka.a.b.2.2, a)')
    'aikavali(...eka.a.b.2, .a)'
    >>> suoritusJoukko('aikavali(...eka.a.b.2, a)')
    'aikavali(...eka.a.b, .a)'
    """
    muokattu= re.sub("(([.][^-,+*/ ]+)+)(\.[^-,+*/)(]*)(?![^-,+*/() ])","\g<1>",s) # poistettavat osat
    muokattu= re.sub("(?<![a-zA-Z.])([a-zA-Z]\w*)(?!\w*[(.])",".\g<1>",muokattu)
    """
    haku= re.finditer("(?<![a-zA-Z.])([a-zA-Z]\w*)(?!\w*[(.])",s)
    muutokset=[]
    for h in haku : # pelkät muuttujat
        uusi= "." + s[h.start():h.end()]
        print uusi
        muutokset.append( (h.start(),h.end(),uusi) )
    muokattu=s[:muutokset[0][0]]
    for i in range(len(muutokset)-1): 
        muokattu=muokattu+muutokset[i][2]
        muokattu=muokattu+s[muutokset[i][1]:muutokset[i+1][0]]
        muokattu=muokattu+muutokset[-1][2]
        muokattu=muokattu+s[muutokset[-1][1]:]
        #muokattu= re.sub("(([.][^-,+*/ ]+)+)(\.[^-,+*/ ]*)(?![^-,+*/ ])","\g<1>",muokattu) # poistettavat osat
    """
    return muokattu

def luoMuuttujat(sarja) :
        """ 
        Luo sarjan syotteiden muuttujasanakirjan:
        rakenne on muotoa: muuttujat[tehtavan_nimi][osatatehtavan_nimi][syotteen_nimi][vartion_nro]=arvo
        mukana olevien vartioista loytyy tieto: muuttujat[tehtavan_nimi]["mukana"][vartion_nro]=1
        """
        dict_teht=[]
        vartiot=sarja.vartio_set.all()
        tehtavat=sarja.tehtava_set.all()
        for t in tehtavat:
                dict_ot=[]
                mukana_olevat=t.mukanaOlevatVartiot()
                dict_m=[]
                for m in mukana_olevat :
                        dict_m.append( (str(m.nro),1)  )
                dict_ot.append(("mukana" , MathDict(dict_m) ) )
                osatehtavat=t.osatehtava_set.all()
                for ot in osatehtavat:
                        dict_maaritteet=[]
                        maaritteet = ot.syotemaarite_set.all()
                        for m in maaritteet:
                                syotteet=m.syote_set.all()
                                dict_syotteet=[]
                                for v in vartiot :
                                        s=syotteet.filter(vartio=v)
                                        if len(s)==1 : 
                                                try :
                                                        dict_syotteet.append((str(v.nro),DictDecimal(s[0].arvo)))
                                                except InvalidOperation: 
                                                        if not s[0].arvo=="kesk":
                                                                dict_syotteet.append((str(v.nro),s[0].arvo))
                                                except TypeError : pass

                                dict_maaritteet.append( (m.nimi,MathDict(dict_syotteet)) )
                        dict_ot.append( (ot.nimi,MathDict(dict_maaritteet)) )
                t_nimi= t.nimi.replace(" ","").replace("!","").lower()
                dict_teht.append( (t_nimi,MathDict(dict_ot)) )
        muuttujat= MathDict(dict_teht)
        return muuttujat

def luoLaskut(sarja) :
        """
        luo kaksiulotteisen taulukon jossa on laskutoimitukset vartion pisteiden laskemiseen.
        """
        vartiot=sarja.vartio_set.all()
        tehtavat=sarja.tehtava_set.all()
        taulukko=[]
        pino=[] # Pinoon laitetaan kulloinenkin iterointipolku jotta muuttujan nimet voidaan muuttaa suhteellisesta kirjaimesta absoluuttiseen polkuun.
        for v in vartiot:
                vartioRivi=[]
                for t in tehtavat:
                        t_nimi= t.nimi.replace(" ","").replace("!","").lower()
                        pino.append(t_nimi)
                        osatehtavat=t.osatehtava_set.all()
                        ot_lauseet=[]
                        for ot in osatehtavat:
                                pino.append(ot.nimi)
                                ot_lause=ot.kaava #.lower() 
                                parametrit=ot.parametri_set.all()
                                maaritteet=ot.syotemaarite_set.all()
                                korvautuu=True
                                # Suora summa syotteiden välillä
                                if ot_lause =="ss" and maaritteet :
                                        ot_lause=""
                                        for m in maaritteet:
                                                ot_lause=ot_lause+m.nimi+"+"
                                        ot_lause=ot_lause[:-1]
                                else :
                                    # Korvataan parametrit
                                    while korvautuu:
                                        korvautuu=False
                                        vanha=ot_lause
                                        for p in parametrit:
                                                ot_lause=re.sub(p.nimi+r"(?!\w+)",p.arvo,ot_lause)
                                        # Pikatie "muk" -> "..mukana" 
                                        ot_lause=re.sub("muk"+r"(?!\w+)","..mukana",ot_lause)
                                        # Muunnos "suor" -> kaikkien vartioiden lasketut suoritukset
                                        try:
                                                vartion_kaava=parametrit.filter(nimi="vartion_kaava")[0].arvo
                                        	vartion_kaava=re.sub("vartio"+r"(?!\w+)", str(v.nro) ,vartion_kaava)

                                                for p in parametrit:
                                                        vartion_kaava=re.sub(p.nimi+r"(?!\w+)",p.arvo,vartion_kaava)
                                                ot_lause=re.sub("suor"+r"(?!\w+)",
                                                                suoritusJoukko(vartion_kaava),
                                                                ot_lause)
                                        except IndexError: pass
                                        if not ot_lause==vanha : korvautuu=True
                                        
                                # Muutetaan muuttujien nimet koko polun mittaisiksi: tehtava(nimi).osatehtava(nimi).syote(nimi).vartio(nro)
                                ot_lause=korvaa(ot_lause,pino,str(v.nro))
                                # Pikatie vartio -> vartion numero
                                ot_lause=re.sub("vartio"+r"(?!\w+)", str(v.nro) ,ot_lause)
				ot_lauseet.append((ot.nimi,ot_lause))
                                pino.pop()
                        tehtava_lause=""
                        #Suora summa osatehtavien välillä:
                        if t.kaava.lower()=="ss" and len(ot_lauseet) :
                                for l in ot_lauseet :
                                        tehtava_lause=tehtava_lause + "max([0,"+l[1]+"])+"
                                tehtava_lause=tehtava_lause[:-1]
                        else:
                                tehtava_lause=t.kaava.lower()
                                for l in ot_lauseet:
                                        lause=l[1]
                                        tehtava_lause=re.sub(r"(?<!\w|[.])"+l[0]+r"(?<![.])(?!\w+)(?![.])","max([0,"+lause+"])",tehtava_lause)
                                
                        vartioRivi.append(tehtava_lause.lower())
                        pino.pop()
                taulukko.append(vartioRivi)
        return taulukko

def laskeSarja(sarja):
        """
        Laskee tulokset halutulle sarjalle. 
        Palauttaa kaksiuloitteisen taulukon[vartio][tehtävä] = pisteet.
        Taulukon ensimmäisissä sarakkeissa on vartio tai tehtävä objekteja muissa pisteitä.
        Taulukon vasemmassa ylänurkassa on sarjan objekti
        """
        #Lasketaan tulokset:
        muuttujat = luoMuuttujat(sarja)
        laskut= luoLaskut(sarja)
        tulokset = laskeTaulukko(laskut,muuttujat)
        #Muokataan oikean muotoinen tulostaulukko:
        vartiot=sarja.vartio_set.all()
        tehtavat=sarja.tehtava_set.all()
        siirrettavat=[]
        for i in range(len(vartiot)):
                # Merkataan tuloksiin H hylättyihin tehtäviin:
                for t in range(len(tulokset[i])) :
                        hylatty=True
                        syotteet= vartiot[i].syote_set.filter(maarite__osa_tehtava__tehtava=tehtavat[t])
                        for s in syotteet:
                                if not s.arvo=="h":  hylatty=False
                        if hylatty and len(syotteet): tulokset[i][t]= "H"

                #Merkataan siirrettäviksi ulkopuolella olevat:
                if not vartiot[i].keskeyttanyt == None or not vartiot[i].ulkopuolella == None : 
                        #Merkataan keskeyttaneille tuloksiin "K" keskeyttämisestä eteenpäin
                        if not vartiot[i].keskeyttanyt==None:
                                kesk=vartiot[i].keskeyttanyt-1
                                for t in range(kesk,len(tulokset[i])) :tulokset[i][t]= "K"
                        siirrettavat.append(i)
                #Tuomarineuvosto:
                vartion_tuomarit=vartiot[i].tuomarineuvostulos_set.all()
                if len( vartion_tuomarit ):
                        for t in range(len(tulokset[i])) :
                                tuom=vartion_tuomarit.filter(tehtava=tehtavat[t])
                                if len(tuom) :
                                        try: 
                                                tulokset[i][t]= Decimal(tuom[0].pisteet)
                                        except:
                                                tulokset[i][t]= tuom[0].pisteet
                #Kokonaispisteet:
                summa=0
                for s in tulokset[i] :
                        if s and type(s)!=str and type(s)!=unicode : summa+= s 
                tulokset[i].insert(0,summa)
                #Vartio objekti jokaisen rivin alkuun:
                tulokset[i].insert(0,vartiot[i])
                        
        # Siirretään ulkopuoliset ja mukana olevat omiin taulukkoihinsa
        mukana=[]
        ulkona=[]
        for i, item in enumerate(tulokset):
                u=False
                for s in siirrettavat:
                        if s==i : u=True
                if u : ulkona.append(item)
                else : mukana.append(item)
        tulokset=mukana

        #Lisätään tehtävärivi ylös
        t_list=[sarja,"Yht." ,]
        pisteet_yhteensa=0
        for t in tehtavat:
                try:
                        if int(t.maksimipisteet) : pisteet_yhteensa+=int(t.maksimipisteet)
                except: pass
                t_list.append(t)
        t_list[0].maksimipisteet=pisteet_yhteensa

        #Tasapisteissä määräävät tehtävät
        tasa1 = 0
        tasa2 = 0
        tasa3 = 0
        if sarja.tasapiste_teht1 : tasa1 = sarja.tasapiste_teht1+1
        if sarja.tasapiste_teht2 : tasa2 = sarja.tasapiste_teht2+1
        if sarja.tasapiste_teht2 : tasa3 = sarja.tasapiste_teht3+1
        
        tulokset.sort(key=operator.itemgetter(1) ,reverse=True)
        ulkona.sort(key=operator.itemgetter(1) ,reverse=True)
        #Järjestetään taulukot
        try :
                tulokset.sort( key=operator.itemgetter(1,tasa1,tasa2,tasa3),reverse=True )
                ulkona.sort( key=operator.itemgetter(1,tasa1,tasa2,tasa3),reverse=True )
        except : # tehtäviä < 3
		pass
        #Lisätään tehtävärivi ylos
        mukana.insert(0,t_list)
        
        return (mukana,ulkona)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

