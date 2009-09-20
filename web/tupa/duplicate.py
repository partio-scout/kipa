from models import *
#coding: latin-1

def kopioiTehtava(tehtava,sarjaan,uusiNimi=None) :
        """
        Kopioi määritellyn tehtävän haluttuun sarjaan.
        """
        # Kopioi itse tehtävä:
        tNimi=tehtava.nimi
        if uusiNimi:
                tNimi=uusiNimi
        uusiTehtava=Tehtava( sarja = sarjaan,
                             nimi = tNimi,
                             kaava = tehtava.kaava,
                             jarjestysnro = tehtava.jarjestysnro )
        uusiTehtava.save()
        
        # Kopioi osatehtavat:
        osatehtavat = tehtava.osatehtava_set.all()
        for ot in osatehtavat:
                uusiot=OsaTehtava(nimi=ot.nimi,
                                kaava=ot.kaava,
                                tyyppi=ot.tyyppi,
                                tehtava=uusiTehtava)
                uusiot.save()
                # Kopioi parametrit
                parametrit = ot.parametri_set.all()
                for p in parametrit :
                        uusip=Parametri(nimi=p.nimi,
                                        arvo=p.arvo ,
                                        osa_tehtava=uusiot)
                        uusip.save()

                # Kopioi määritteet:
                maaritteet = ot.syotemaarite_set.all()
                for m in maaritteet:
                        uusim=SyoteMaarite( nimi=m.nimi,
                                    osa_tehtava=uusiot,
                                    tyyppi=m.tyyppi,
                                    kali_vihje=m.kali_vihje )
                        uusim.save()
        
        nimi = models.CharField(max_length=255)
        kali_vihje = models.CharField(max_length=255, blank=True , null=True )
        osa_tehtava = models.ForeignKey(OsaTehtava)






