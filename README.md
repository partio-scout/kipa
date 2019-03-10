Kipa
====

Kipa- / Tupa2-ohjelmisto, jota käytetään partiotaitokilpailujen tuloslaskentaan. https://www.facebook.com/Kisapalvelu/

Asennusohjeet: https://sites.google.com/site/kisapalvelukipa/kaeytae-ja-asenna

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
* testit (parametrit ei välity)
* migrate
* käyttäjäautentikointi (serverilaajuinen)
* piirienväliset pisteet
* dia2django
* production serveri (nginx ja uwsgi)

**Ei toimi tai ei testattu:**

* HTTPS tarvii sertifikaatit web-serverille
* i18n
* muut turhat härpäkkeet, joita en osaa käyttää

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
