import models 

def kisa_xml(kisa):
        """
        Apufunktio -> Luo xml merkkijonon kaikista kisan objekteista.
        Jattaa henkilot ja allergiat luomatta.
        """
        from django.core import serializers
        objects=[kisa,]
        for s in kisa.sarja_set.all():
                objects.append(s)
                for v in s.vartio_set.all():
                        objects.append(v)
                for t in s.tehtava_set.all():
                        objects.append(t)
                        for te in t.testaustulos_set.all():
                                objects.append(te)
                        for tt in t.tuomarineuvostulos_set.all():
                                objects.append(tt)
                        for ot in t.osatehtava_set.all() :
                                for sm in ot.syotemaarite_set.all():
                                        objects.append(sm)
                                        for s in sm.syote_set.all():
                                                objects.append(s)
                                for p in ot.parametri_set.all():
                                        objects.append(p)
                                objects.append(ot)
        return serializers.serialize("xml", objects , indent=4)

def kopioiTehtava(tehtava,sarjaan,uusiNimi=None) :
        """
        Kopioi maaritellyn tehtavan haluttuun sarjaan.
        """
        # Kopioi itse tehtava:
        tNimi=tehtava.nimi
        if uusiNimi:
                tNimi=uusiNimi
        uusiTehtava=models.Tehtava( sarja = sarjaan,
                             nimi = tNimi,
                             kaava = tehtava.kaava,
                             jarjestysnro = tehtava.jarjestysnro )
        uusiTehtava.save()
        
        # Kopioi osatehtavat:
        osatehtavat = tehtava.osatehtava_set.all()
        for ot in osatehtavat:
                uusiot=models.OsaTehtava(nimi=ot.nimi,
                                kaava=ot.kaava,
                                tyyppi=ot.tyyppi,
                                tehtava=uusiTehtava)
                uusiot.save()
                # Kopioi parametrit
                parametrit = ot.parametri_set.all()
                for p in parametrit :
                        uusip=models.Parametri(nimi=p.nimi,
                                        arvo=p.arvo ,
                                        osa_tehtava=uusiot)
                        uusip.save()

                # Kopioi maaritteet:
                maaritteet = ot.syotemaarite_set.all()
                for m in maaritteet:
                        uusim=models.SyoteMaarite( nimi=m.nimi,
                                    osa_tehtava=uusiot,
                                    tyyppi=m.tyyppi,
                                    kali_vihje=m.kali_vihje )
                        uusim.save()
        

