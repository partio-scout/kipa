'''Kisan alasivujen URLit ja sivujen otsikot'''
# -*- coding: utf-8 -*-

# Testikisan nimimääritys, oletusarvona: testikisa
TESTIKISA = u'testikisa'

# Kipa pääsivu

KIPA_OTSIKKO = u'Kipa - kaikki kisat'
KIPA_URL = u'http://127.0.0.1:8000/kipa'

#Suoritusten syöttö

TULOSTEN_SYOTTO_OTSIKKO = u'Kipa - Syötä tuloksia'
TULOSTEN_SYOTTO_URL = u'syota'

TULOSTEN_SYOTTO_TARKISTUS_OTSIKKO = u'Kipa - Syötä\
 tuloksia - tarkistussyötteet'
TULOSTEN_SYOTTO_TARKISTUS_URL = u'syota/tarkistus'

#Tulokset

TULOSTEN_TARKISTUS_OTSIKKO = u'Kipa - Tulokset sarjoittain'
TULOSTEN_TARKISTUS_URL = u'tulosta/normaali'

TUOMARINEUVOSTO_OTSIKKO = u'Kipa - Tuomarineuvoston antamien\
 tulosten määritys'
TUOMARINEUVOSTO_URL = u'maarita/tuomarineuvos'

LASKENNAN_TILANNE_OTSIKKO = u'Kipa - Tulokset sarjoittain'
LASKENNAN_TILANNE_URL = u'tulosta/tilanne'


#Kisan Määritykset

KISAN_MAARITYS_OTSIKKO = u'Kipa - Määritä kisa'
KISAN_MAARITYS_URL = u'maarita'

VARTIOIDEN_MAARITYS_OTSIKKO = u'Kipa - Määritä vartiot'
VARTIOIDEN_MAARITYS_URL = u'maarita/vartiot'

TEHTAVAN_MAARITYS_OTSIKKO = u'Kipa - Muokkaa tehtävää'
TEHTAVAN_MAARITYS_URL = u'maarita/tehtava'

TESTITULOKSIEN_MAARITYS_OTSIKKO = u'Kipa - Testituloksien määritys'
TESTITULOKSIEN_MAARITYS_URL = u'maarita/testitulos'

#Ylläpito

# huom Listaa kaikki kisat linkki vie pääsivulle
KAIKKI_KISAT_OTSIKKO = u'Kipa - kaikki kisat'
KAIKKI_KISAT_URL = KIPA_OTSIKKO

# Tallenna kisa, ei vielä osaamista filen vastaanottoon, TBD
#"http://127.0.0.1:8000/kipa/testi_kisa/tallenna/

# Kisan tuonti tiedostosta, tod.näk helppoa käyttämällä fixtuuria.TBD 
KISAN_TUONTI_URL = u'korvaa'
KISAN_TUONTI_OTSIKKO = u'Kipa - Korvaa kisa tiedostosta'

# Poista Kisa
KISAN_POISTO_OTSIKKO = u'Kipa - Poista kisa'
KISAN_POISTO_URL = u'poista'

# Autentikointi
admin_tunnus = u'admin'
admin_salasana = u'admin'
