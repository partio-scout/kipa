Kipa
====

Kipa- / Tupa2-ohjelmisto, jota käytetään partiotaitokilpailujen tuloslaskentaan. https://www.facebook.com/Kisapalvelu/

Asennusohjeet, Linux: docs/kipa asennusmuistio ubuntu 2017.txt
Windows: https://sites.google.com/site/kisapalvelukipa/kaeytae-ja-asenna

Vanhat sivustot:

* https://sites.google.com/site/kisapalvelukipa/
* http://sourceforge.net/projects/tupa2/

**Ohjelmaa kokeiltu:**

* Django v.1.11
* Python v.2.7
* Chrome / Firefox

**Tilanne: toimivat**

* Kipa -sivusto
* Admin -sivusto
* static files
* migrate
* käyttäjäautentikointi (serverilaajuinen)
* piirienväliset pisteet
* dia2django
* production serveri (nginx ja uwsgi)

**Ei toimi tai ei testattu:**

* testit (käyttäjähallinta ei mukana ja parametrit ei välity)
* HTTPS tarvii sertifikaatit web-serverille
* i18n
* muut turhat härpäkkeet, joita en osaa käyttää

**Tunnetut, ei toivotut ominaisuudet (known bugs):**

* Jossain harvoissa tilanteissa, samassa sarjassa olevat samannimiset vartiot saavat samat tulokset, riippumatta syötteistä.
* Samassa sarjassa olevat samannimiset tehtävät saavat toisetensa tulokset tulosten laskennassa.
* Jos interpoloinnissa on vain yksi vartio ja nollasuorituksen kaavana max*muk, niin ainut vartio saa 0 pistettä.
* Yhteen tehtävään voi syöttää vain yksi käyttäjä kerrallaan, joko varsinaisia tai tarkistussyötteitä.
* Negatiivinen aikaväli antaa tulokseski nollan.
* Aika -syötekentässä, E- tai H- syöte rikkoo ajan muotoilun, mutta korjaantuu tallentamalla 0 (tai joku) aika.
* Tehtävän kaavassa desimaalipilkku kaataa laskennan (kaavan tarkastus ei aukoton).

**Toivotut ominaisuudet:**

* Python 3 ja Django 2 -tuki
* Docker container
* Manuaalin päivittäminen
* Vartioiden import taulukosta / Kuksasta (tai muusta ilmoittautumisjärjestelmästä)
* Tuloslaskennan huomiot, tuomarineuvoston kirjaukset, kilpailijoiden tarkastuspyynnöt tehtävien / syötteiden yhteyteen
* Tietojen tallennus taustalla
* Tietojen varmuuskopiointi ja palautus, eli Undo / muutosten logaus
* Kisan tilanneseuranta
* Piirit ja lippukunnat valita listasta, ei kirjoittamalla -> lyhenteet
* Tulosten massavienti tikulle, eli yhdestä napista kaikki formaatit ja sarjat
* Tulosten näyttämiseen tykillä valinta, mitkä sarjat + piirien tilanne ja onko useampi sarja samalla sivulla
* Mahdollisuus liittää kuvia (videota?) tulosten tarkastuksen yhteyteen / kommentteihin
* Tulosseuranta / tilanneseuranta netin yli kotiväelle

**Muita ohjeita:**
* Tietokantatiedostojen (.dia) katselemiseen ja muokkaamiseen voit käyttää ilmaista 'Dia Diagram Editor' -ohjelmaa. https://sourceforge.net/projects/dia-installer/ (asennus debian/ubuntu ympäristössä: sudo apt-get install dia )

* Dia2django -skriptin käyttö:
  * Mene omaan kipa kansioon ...kipa/web/tupa/
  * Aja komento: python dia2django.py tietokanta.dia models.py
  * Skripti päivittää ohjelman models.py tiedoston tietokantakentät annetun .dia tiedoston mukaiseksi.

Lisenssi
========

Tämä ohjelma on vapaa; tätä ohjelmaa on sallittu levittää edelleen ja muuttaa GNU yleisen lisenssin (GPL-lisenssin) ehtojen mukaan sellaisina kuin Free Software Foundation on ne julkaissut Lisenssin version 3 mukaisesti.

Tätä ohjelmaa levitetään siinä toivossa, että se olisi hyödyllinen, mutta ilman mitään takuuta; ilman edes hiljaista takuuta kaupallisesti hyväksyttävästä laadusta tai soveltuvuudesta tiettyyn tarkoitukseen. Katso GPL-lisenssistä lisää yksityiskohtia.

Tämän ohjelman mukana pitäisi tulla kopio GPL-lisenssistä; jos näin ei ole, kirjoita osoitteeseen Free Software Foundation Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
