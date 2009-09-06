from models import *
#coding: latin-1

def kopioiTehtava(tehtava,sarjaan,uusiNimi=None) :
        # Kopioi itse tehtävä:
        tNimi=tehtava.nimi
        if uusiNimi:
                tNimi=uusiNimi
        uusiTehtava=Tehtava( sarja = sarjaan,
                             nimi = tNimi,
                             kaava = tehtava.kaava,
                             jarjestysnro = tehtava.jarjestysnro )
        uusiTehtava.save()

        # Kopioi määritteet:
        maaritteet = tehtava.syotemaarite_set.all()
        for m in maaritteet:
                uusim=SyoteMaarite( nimi=m.nimi,
                                    tehtava=uusiTehtava,
                                    tyyppi=m.tyyppi,
                                    kali_vihje=m.kali_vihje )
                uusim.save()
        
        # Kopioi kaavat:
        kaavat = tehtava.osapistekaava_set.all()
        for k in kaavat:
                uusik=OsapisteKaava(nimi=k.nimi,kaava=k.kaava,tehtava=uusiTehtava)
                uusik.save()






