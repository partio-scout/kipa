# Kipan asennus omalle koneelle

Tämä ohje neuvoo askel askeleelta, miten Kipa asennetaan omalle
tietokoneelle (Windows, Mac tai Linux). Aiempaa kokemusta ei tarvita.
Ohjeen kaikki komennot kirjoitetaan **komentoriville**:

* **Windows:** paina Käynnistä-painiketta, kirjoita `PowerShell` ja avaa se.
* **Mac:** paina `Cmd + välilyönti`, kirjoita `Pääte` (tai `Terminal`) ja avaa se.
* **Linux:** avaa `Pääte` / `Terminal`.

Kirjoita (tai kopioi) komento ja paina `Enter`. Rivit, jotka alkavat
`#`-merkillä, ovat selityksiä, eikä niitä tarvitse kirjoittaa.

Kipa pyörii koneella kahdessa **Docker-kontissa**: toisessa on itse Kipa ja
toisessa MySQL-tietokanta, johon kisojen tiedot tallentuvat. Docker hoitaa
kaiken muun, joten Pythonia tai tietokantaa ei tarvitse asentaa erikseen.

---

## 1. Asenna Docker

### Windows ja Mac

1. Mene osoitteeseen https://www.docker.com/products/docker-desktop/
2. Lataa **Docker Desktop** omalle käyttöjärjestelmällesi.
   * Macilla valitse **Apple Silicon** (M1, M2, M3…) tai **Intel** sen
     mukaan, mikä koneessasi on (Omena-valikko → *Tietoja tästä Macista*).
3. Asenna ohjelma normaalisti ja hyväksy oletusasetukset.
   * Windows saattaa pyytää asentamaan **WSL**-päivityksen ja käynnistämään
     koneen uudelleen. Tee niin.
4. Käynnistä **Docker Desktop**. Sen voi ohittaa kirjautumatta
   (*Skip* / *Continue without signing in*).
5. Odota, kunnes Docker Desktopin vasemmassa alakulmassa lukee
   *Engine running* (vihreä).

### Linux (Ubuntu)

```sh
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

Kirjaudu tämän jälkeen ulos ja takaisin sisään (tai käynnistä kone
uudelleen).

### Tarkista, että Docker toimii

```sh
docker --version
docker compose version
```

Molempien pitäisi tulostaa versionumero. Jos tulee virhe, varmista että
Docker Desktop on käynnissä.

---

## 2. Asenna Git

Gitillä ladataan Kipan tiedostot ja myöhemmin päivitykset.

* **Windows:** lataa ja asenna https://git-scm.com/download/win
  oletusasetuksilla. **Sulje PowerShell ja avaa se uudelleen** asennuksen
  jälkeen.
* **Mac:** kirjoita päätteeseen `git --version`. Jos Git puuttuu, Mac
  tarjoaa asentaa sen (*Asenna* / *Install*).
* **Linux:** `sudo apt install git`

Tarkista:

```sh
git --version
```

---

## 3. Lataa Kipa

Tämä luo kotihakemistoosi `kipa`-kansion, jossa on Kipan tiedostot.

```sh
cd ~
git clone -b Kipa_With_MySQL https://github.com/mikkolindfors/kipa.git
cd kipa
```

> **Ilman Gitiä:** voit myös ladata ZIP-paketin osoitteesta
> https://github.com/mikkolindfors/kipa/tree/Kipa_With_MySQL
> (vihreä *Code*-nappi → *Download ZIP*) ja purkaa sen. Päivittäminen on
> silloin kuitenkin hankalampaa.

---

## 4. Aseta salasanat

Kipa lukee salasanat `.env`-nimisestä tiedostosta. Tee se mallitiedostosta:

* **Windows:** `copy .env.example .env`
* **Mac ja Linux:** `cp .env.example .env`

Avaa tiedosto muokattavaksi:

* **Windows:** `notepad .env`
* **Mac:** `open -e .env`
* **Linux:** `nano .env` (tallennus `Ctrl + O`, `Enter`, poistu `Ctrl + X`)

Vaihda kaikki kolme `vaihdaTama…`-salasanaa omiksesi ja tallenna tiedosto.

* Käytä vain kirjaimia ja numeroita.
* `KIPA_ADMIN_USER` ja `KIPA_ADMIN_PASSWORD` ovat tunnukset, joilla
  kirjaudut Kipaan pääkäyttäjänä. **Kirjoita ne muistiin.**
* Tietokannan salasanoja (`KIPA_DB_PASSWORD`, `MYSQL_ROOT_PASSWORD`) **ei
  saa vaihtaa** enää ensimmäisen käynnistyksen jälkeen, muuten Kipa ei
  saa yhteyttä tietokantaan.

---

## 5. Käynnistä Kipa

Varmista, että olet `kipa`-kansiossa, ja aja:

```sh
docker compose up -d --build
```

Ensimmäinen käynnistys kestää useita minuutteja, koska Docker lataa ja
rakentaa tarvittavat osat. Seuraavat käynnistykset ovat nopeita.

Kun komento on valmis, tarkista tilanne:

```sh
docker compose ps
```

Molempien rivien (`db` ja `kipa`) tilana pitäisi olla *running* tai *Up*.

---

## 6. Avaa Kipa selaimessa

Avaa selaimella osoite **http://localhost:8000/kipa/**

1. Kirjaudu oikeasta yläkulmasta vaiheessa 4 asettamillasi
   pääkäyttäjän tunnuksilla.
2. Luo kisa kohdasta **Luo uusi kisa**.

### Muiden käyttäjien lisääminen

1. Klikkaa yläpalkista **Käyttäjien hallinta** (tai mene osoitteeseen
   http://localhost:8000/admin/).
2. Valitse **Käyttäjät** → **Lisää käyttäjä**, anna tunnus ja salasana ja
   tallenna.
3. Käyttäjän sivun alareunassa kohdassa **Näkyvät kisat ja oikeustaso**
   valitaan, mitkä kisat hänelle näkyvät ja millä tasolla:
   * **Tulokset:** näkee tulokset
   * **Syöttö:** voi myös syöttää suorituksia
   * **Määritys:** voi myös muokata sarjoja, vartioita ja tehtäviä
   * **Ylläpito:** voi myös palauttaa ja poistaa kisan
4. Tallenna.

Jokainen kirjautunut käyttäjä voi myös luoda omia kisoja.

---

## 7. Käyttö muilta koneilta (lähiverkko)

Kipaa voi käyttää samaan aikaan monelta koneelta, puhelimelta tai
tabletilta. Kaikkien laitteiden pitää olla **samassa verkossa** (sama
Wi-Fi tai reititin) kuin Kipaa pyörittävä kone.

### Selvitä Kipa-koneen osoite

* **Windows:** aja `ipconfig` ja katso Wi-Fi- tai Ethernet-sovittimen
  kohta **IPv4 Address** (esim. `192.168.1.23`). Älä käytä
  *vEthernet (WSL)* -kohdan osoitetta.
* **Mac:** aja `ipconfig getifaddr en0` (Wi-Fi). Jos tulos on tyhjä,
  kokeile `ipconfig getifaddr en1`.
* **Linux:** aja `hostname -I` ja käytä ensimmäistä osoitetta.

### Avaa Kipa toisella laitteella

Kirjoita toisen laitteen selaimeen Kipa-koneen osoite, esimerkiksi
**http://192.168.1.23:8000/kipa/**

Jokainen käyttäjä kirjautuu omilla tunnuksillaan (ks. *Muiden
käyttäjien lisääminen* yllä).

### Jos yhteys ei toimi

* **"Bad Request (400)"**: `.env`-tiedostossa pitää olla
  `KIPA_ALLOWED_HOSTS=*` (tai Kipa-koneen osoite). Muutoksen jälkeen aja
  `docker compose up -d`.
* **Sivu ei lataudu lainkaan**: tarkista, että laitteet ovat samassa
  verkossa. Windows kysyy ensimmäisellä kerralla, sallitaanko Dockerin
  liikenne palomuurin läpi. Salli se **yksityisissä verkoissa**
  (*Private networks*). Varmista myös, että Windowsin verkkoprofiiliksi
  on valittu *Yksityinen* eikä *Julkinen* (*Asetukset → Verkko ja
  Internet → Wi-Fi → verkon ominaisuudet*). Macilla palomuuri on
  yleensä pois päältä. Jos se on päällä, salli Dockerin yhteydet.
* **Osoite vaihtui**: reititin voi antaa koneelle uuden osoitteen
  esimerkiksi uudelleenkäynnistyksen jälkeen. Tarkista osoite uudelleen
  yllä olevilla ohjeilla.
* **Työpaikan kone**: työkoneiden VPN tai tietoturvaohjelmat estävät
  usein kaikki muilta koneilta tulevat yhteydet. Käytä silloin Kipa-koneena
  omaa konetta tai katkaise VPN kisan ajaksi.

> Kipa käyttää lähiverkossa salaamatonta http-yhteyttä. Älä käytä
> Kipaa julkisessa tai vieraassa Wi-Fi-verkossa, vaan omassa reitittimessäsi
> tai kisatoimiston verkossa.

---

## Päivittäinen käyttö

Kaikki komennot ajetaan `kipa`-kansiossa (`cd ~/kipa`).

| Mitä haluat tehdä | Komento |
|---|---|
| Sammuttaa Kipan | `docker compose stop` |
| Käynnistää Kipan uudelleen | `docker compose start` |
| Katsoa, onko Kipa käynnissä | `docker compose ps` |
| Katsoa Kipan lokeja (lopetus `Ctrl + C`) | `docker compose logs -f kipa` |

Kipa käynnistyy automaattisesti aina, kun Docker käynnistyy. Docker
Desktopin asetuksista (*Settings → General → Start Docker Desktop when you
sign in*) voit valita, käynnistyykö Docker koneen käynnistyessä.

Kisojen tiedot säilyvät tallessa, vaikka Kipan tai koneen sammuttaisi.

Jos muutat `.env`-tiedostoa, ota muutos käyttöön komennolla
`docker compose up -d` (pelkkä `start` ei lue muutoksia).

---

## Päivittäminen uuteen versioon

```sh
cd ~/kipa
git pull
docker compose up -d --build
```

Kisat säilyvät päivityksessä. Kaikkien käyttäjien pitää kirjautua
päivityksen jälkeen uudelleen.

---

## Varmuuskopiointi

**Yksittäinen kisa:** avaa kisa Kipassa ja valitse *Ylläpito → tallenna
kisa*. Saat XML-tiedoston, jonka voi palauttaa kohdasta *palauta kisa* tai
etusivun *Lisää kisa tiedostosta*.

**Koko tietokanta** (kaikki kisat ja käyttäjät):

```sh
docker compose exec db sh -c 'mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" kipa > /tmp/kipa.sql'
docker compose cp db:/tmp/kipa.sql kipa-varmuuskopio.sql
```

Tiedosto `kipa-varmuuskopio.sql` ilmestyy `kipa`-kansioon. Kopioi se
talteen esimerkiksi muistitikulle. Varoitus *"Using a password on the
command line interface can be insecure"* on tässä harmiton.

Palautus varmuuskopiosta (**korvaa nykyiset tiedot**):

```sh
docker compose cp kipa-varmuuskopio.sql db:/tmp/kipa.sql
docker compose exec db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" kipa < /tmp/kipa.sql'
```

---

## Ongelmatilanteita

**"Cannot connect to the Docker daemon" tai "docker: command not found"**
Docker Desktop ei ole käynnissä. Käynnistä se ja odota, kunnes siinä lukee
*Engine running*.

**"Set KIPA_DB_PASSWORD"**
`.env`-tiedosto puuttuu tai et ole `kipa`-kansiossa. Tee vaihe 4 ja aja
komento `kipa`-kansiossa.

**"port is already allocated" / "address already in use"**
Jokin muu ohjelma käyttää jo porttia 8000. Jos koneella on vanha Kipa
käynnissä, sammuta se: `docker stop kipa`. Muuten avaa
`docker-compose.yml` tekstieditorilla, vaihda rivi `- "8000:80"` muotoon
`- "8080:80"` ja käytä osoitetta http://localhost:8080/kipa/.

**Sivu ei aukea heti käynnistyksen jälkeen**
Odota hetki. Kipa odottaa, että tietokanta on valmis. Tilanteen näkee
komennolla `docker compose logs -f kipa`.

**Pääkäyttäjän salasana unohtui**

```sh
docker compose exec kipa python manage.py changepassword admin
```

(Vaihda `admin` tilalle oma pääkäyttäjätunnuksesi, jos se on eri.)

**Kirjautuminen ei onnistu, vaikka tunnukset ovat oikein**
Pääkäyttäjä luodaan vain ensimmäisellä käynnistyksellä. Jos muutit
`KIPA_ADMIN_USER`- tai `KIPA_ADMIN_PASSWORD`-arvoa myöhemmin, käytä
alkuperäisiä tunnuksia tai vaihda salasana yllä olevalla komennolla.

---

## Kipan poistaminen koneelta

```sh
cd ~/kipa
docker compose down
```

Tämä poistaa kontit mutta **säilyttää kisojen tiedot**. Jos haluat poistaa
myös kaikki tiedot pysyvästi, ota ensin varmuuskopio ja aja sitten
`docker compose down -v`.
