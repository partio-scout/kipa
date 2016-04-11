# !/usr/bin/env python
# -*- coding: utf-8 -*-
# KiPa(KisaPalvelu), tuloslaskentajarjestelma partiotaitokilpailuihin
#    Copyright (C) 2016  Espoon models.Partiotuki ry. ept@partio.fi
"""
Yritetään tulevaisuudessa päästä wildcard-importeista eroon. Helpottaa
jatkokehitystä huomattavasti kun tiettää ilman ack:ia missä joku funktio
tai luokka määritellään.
"""
import time
import random
from decimal import Decimal

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponse
from django import template
from django.template import RequestContext
from django.utils.safestring import SafeText
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import DatabaseError

from . import models
from . import forms
from .tehtavanmaaritys import tehtavanMaaritysForm, tallennaTehtavaData


def loginSivu(request):
    if request.method == "POST":
        posti = request.POST
        user = authenticate(username=posti["uname"], password=posti["pword"])
        if user and user.is_active:
            login(request, user)
            messages.success(request, "Heippa " + user.first_name + "!")
        else:
            messages.error(request, "Kirjautuminen epäonnistui")

    return redirect("/kipa/")


def logoutSivu(request):
    logout(request)
    return redirect("/kipa/")


register = template.Library()  # noqa


@register.filter(name="alaviiva")
def cut(value):
    return value.replace("_", " ")


def tarkistaVirhe(syote):
    syottovirhe = None
    if syote and syote.arvo and syote.tarkistus or syote and syote.tarkistus:
        if not syote.arvo == syote.tarkistus:
            try:
                if not Decimal(syote.arvo) == Decimal(syote.tarkistus):
                    syottovirhe = "virhe"
            except:
                syottovirhe = "virhe"
    return syottovirhe


def tehtavanTilanne(tehtava):
    vartioita = tehtava.sarja.vartio_set.all().count()
    syotteita = (models.Syote.objects
                 .filter(maarite__osa_tehtava__tehtava=tehtava)
                 .exclude(arvo="kesk").count())
    kesk_syotteita = (models.Syote.objects
                      .filter(maarite__osa_tehtava__tehtava=tehtava)
                      .filter(arvo="kesk").count())
    maaritteita = (models.SyoteMaarite.objects
                   .filter(osa_tehtava__tehtava=tehtava).count())
    tila = ("a", tehtava.nimi)
    if syotteita:
        tila = ("o", tehtava.nimi)
    if syotteita == vartioita * maaritteita - kesk_syotteita:
        tila = ("s", tehtava.nimi)
    if tehtava.tarkistettu:
        tila = ("t", tehtava.nimi)
    return tila


def testaa_tietokanta():
    kisa = models.Kisa(nimi="tietokantatesti", tunnistus=False)
    try:
        kisa.save()
        kisa.paikka = "a"
        kisa.delete()
        return False
    except DatabaseError:
        return True


def etusivu(request):
    """
    Kipan päävalikko.

    """
    kisat = models.Kisa.objects.all()

    vanha_tietokanta = testaa_tietokanta()
    if vanha_tietokanta:
        kisat = None
    return render_to_response("tupa/index.html",
                              {"vanha_tietokanta": vanha_tietokanta,
                               "object_list": kisat},
                              context_instance=RequestContext(request))


# @permission_required("tupa.change_kisa")
def kisa(request, kisa_nimi):
    """
    models.Kisakohtainen päävalikko.
    """
    kisa = get_object_or_404(models.Kisa, nimi=kisa_nimi)
    vanha_tietokanta = testaa_tietokanta()

    for s in kisa.sarja_set.all():
        s.laskeTulokset()  # tulosten taustalaskenta

    return render_to_response("tupa/kisa.html",
                              {"kisa": kisa,
                               "kisa_nimi": kisa_nimi,
                               "heading": "Etusivu",
                               "vanha_tietokanta": vanha_tietokanta},
                              context_instance=RequestContext(request))


def tulosta(request, kisa_nimi, tulostyyppi=""):
    """
    Valintalista kisan sarjojen tuloksista.
    """
    if len(tulostyyppi):
        tulostyyppi += "/"
    sarjat = models.Sarja.objects.select_related().filter(kisa__nimi=kisa_nimi)
    return render_to_response("tupa/tulosta.html",
                              {"sarja_list": sarjat,
                               "kisa_nimi": kisa_nimi,
                               "tulostyyppi": tulostyyppi,
                               "heading": "Tulokset sarjoittain"},
                              context_instance=RequestContext(request))


def maaritaKisa(request, kisa_nimi=None):
    """
    Määritetään kisa ja sarjat
    """
    if request.method == "POST":
        try:
            kisa = models.Kisa.objects.get(nimi=request.POST['nimi'])
        except models.Kisa.DoesNotExist:
            kisa = models.Kisa(nimi=request.POST['nimi'])
        kisaForm = forms.KisaForm(request.POST, instance=kisa)
        if kisaForm.is_valid():
            kisa = kisaForm.save()
            sarjaForms = forms.SarjaFormset(request.POST, instance=kisa)
            for form in sarjaForms:
                if form.is_valid():
                    sarja = form.save()
                    if sarja.nimi == "":
                        sarja.delete()
            return redirect("/kipa/" + kisa.nimi)
    else:
        kisa = models.Kisa(nimi="")
        if kisa_nimi:
            kisa = get_object_or_404(Kisa, nimi=kisa_nimi)
        sarjaFormit = forms.SarjaFormset(instance=kisa)
        return render_to_response("tupa/maarita.html",
                                  {"heading": "Määritä kisa",
                                   "form": forms.KisaForm(instance=kisa),
                                   "formset": sarjaFormit,
                                   "kisa_nimi": kisa_nimi,
                                   "talletettu": ""},
                                  context_instance=RequestContext(request))
    return redirect("/kipa/")


def maaritaValitseTehtava(request, kisa_nimi):
    """
    Valitsee tehtävän määritettäväksi.
    """
    # Post data
    posti = None
    if request.method == "POST":
            posti = request.POST

    sarjat = models.Sarja.objects.filter(kisa__nimi=kisa_nimi)
    taulukko = []
    for s in sarjat:
        prefix = "sarja" + str(s.id) + '_'
        queryset = models.Tehtava.objects.filter(sarja=s)
        formsetti = forms.TehtavaLinkkiListaFormset(posti,
                                                    queryset=queryset,
                                                    prefix=prefix)
        formsetti.otsikko = s.nimi
        formsetti.id = s.id

        if posti and formsetti.is_valid():
            formsetti.save()
        else:
            taulukko.append(formsetti)

    if posti:
        return redirect("/kipa/" + kisa_nimi + "/maarita/tehtava/")
    else:
        return render_to_response("tupa/maaritaValitseTehtava.html",
                                  {"taulukko": taulukko,
                                   "heading": u"Muokkaa tehtävää",
                                   "kisa_nimi": kisa_nimi},
                                  context_instance=RequestContext(request))


def maaritaVartiot(request, kisa_nimi, talletettu=None):
    """
    Määrittää kisan vartiot sarjoittain.
    """
    sarjat = models.Sarja.objects.filter(kisa__nimi=kisa_nimi)
    # sarjaVartiot = []
    posti = None
    post_ok = True
    # taulukko joka tulee sisältämään vartioiden formeja sarjoittain.
    taulukko = []
    if request.method == "POST":
        posti = request.POST

    for s in sarjat:
        # Luodaan kasa vartioformeja sarjalle
        vartioFormit = models.VartioFormset(posti, instance=s, prefix=s.nimi)
        if vartioFormit.is_valid():  # Katsotaan onko data oikein
            vartioFormit.save()
        else:  # Syöttö perseellään.
            post_ok = False
        vartioFormit.otsikko = s.nimi
        vartioFormit.id = s.id
        taulukko.append(vartioFormit)

    if posti and post_ok:  # Talletetaanko?
        if "nappi" in posti.keys() and posti["nappi"] == "ohjaus":
            return redirect("/kipa/" + kisa_nimi + "/maarita/tehtava/")
        return redirect("/kipa/" + kisa_nimi + "/maarita/vartiot/talletettu/")
    else:  # Ei tallennusta
        tal = ""
        if talletettu == "talletettu" and not posti:
            tal = "Talletettu!"  # Talletettu info yläpalkkiin.
        ohjaus_nappi = None
        request_meta = request.META["HTTP_REFERER"][-23:]
        maaritys = "/kipa/uusiKisa/maarita/"
        if "HTTP_REFERER" in request.META.keys() and request_meta == maaritys:
            # Ensimmäisellä talletuksella näkyy siirry nappi.
            ohjaus_nappi = "siirry tehtävien määritykseen"
            return render_to_response("tupa/valitse_formset.html",
                                      {"taulukko": taulukko,
                                       "heading": "Määritä vartiot",
                                       "kisa_nimi": kisa_nimi,
                                       "talletettu": tal,
                                       "ohjaus_nappi": ohjaus_nappi},
                                      context_instance=RequestContext(request))


def maaritaTehtava(request, kisa_nimi,
                   tehtava_id=None, sarja_id=None, talletettu=""):
    """
    Määritää tehtävän.
    models.Parametrit:
            -kisa_nimi:en lisäksi täytyy määrittää joko tehtävä_id tai sarja_id
            -kun tehtava_id on määritelty, muokataan sen mukaista tehtävää
            -muuten luodaan uutta tehtävää halutulle sarjalle
    """
    posti = None
    if request.method == "POST":
            posti = request.POST

    tehtava = None
    sarja = None
    # Tabs:
    daatta = {}
    if tehtava_id:  # Muokataan vanhaa tehtävää
            tehtava = get_object_or_404(models.Tehtava, id=tehtava_id)
            sarja = tehtava.sarja
            # osatehtavat = tehtava.osatehtava_set.all()
            # alkudata tehtävänmääritysformihässäkälle.
            daatta = luoTehtavaData([tehtava])
    else:  # Luodaan uutta tehtävää
        sarja = get_object_or_404(models.Sarja, id=sarja_id)
        tehtava = models.Tehtava(sarja)

    # Haetaan suurin kaytosssa oleva jarjestysnro tassa sarjassa:
    sarjan_tehtavat = models.Tehtava.objects.filter(sarja=sarja)
    nro = 0  # Uuden tehtävän aloitus järjestysnro.
    for t in sarjan_tehtavat:
        if nro < t.jarjestysnro:
            nro = t.jarjestysnro

    # Luodaan tehtavan maaritys form
    tehtavaForm = tehtavanMaaritysForm(posti,
                                       daatta,
                                       sarja_id=sarja_id,
                                       suurin_jarjestysnro=nro,
                                       tags={"kisa_nimi": kisa_nimi,
                                             "tehtava_id": tehtava_id})

    # Tallennetaan formin muokkaama data
    tehtava_id = tallennaTehtavaData(daatta)

    # sarja.laskeTulokset() # Taustalaskenta

    otsikko = u"Uusi tehtävä" + " (" + sarja.nimi + ")"

    if tehtava and not tehtava.nimi == "":
        otsikko = unicode(tehtava.nimi) + " (" + sarja.nimi + ")"

    # Talletetaanko ja siirrytäänkö talletettu sivuun?
    if posti and "lisaa_maaritteita" not in posti.keys() and daatta["valid"]:
        # Talleta ja luo uusi.
        if "nappi" in posti.keys() and posti["nappi"] == "ohjaus":
            return redirect("/kipa/" + kisa_nimi +
                            "/maarita/tehtava/uusi/sarja/" + str(sarja.id) +
                            "/")

        return redirect("/kipa/" + kisa_nimi + "/maarita/tehtava/" +
                        str(tehtava_id) +
                        "/talletettu/")
    else:  # Ei talletusta tällä kertaa
        tal = ""
        if talletettu == "talletettu" and not posti:
            tal = "Talletettu!"  # Edellisellä sivulla talletettu
        return render_to_response("tupa/maarita.html",
                                  {"forms": [tehtavaForm],
                                   "heading": otsikko,
                                   "kisa_nimi": kisa_nimi,
                                   "tehtava_ida": 5,
                                   "talletettu": tal,
                                   "ohjaus_nappi": "lisää uusi tehtävä",
                                   "taakse": {"title": u"Muokkaa tehtävää",
                                              "url": "/kipa/" +
                                                     kisa_nimi +
                                                     "/maarita/tehtava/"}},
                                  context_instance=RequestContext(request))


def syotaKisa(request, kisa_nimi, tarkistus=None):
    """
    Valitsee kisan tehtävän jonka tuloksia ruvetaan syöttämään.
    """
    if tarkistus:
        otsikko = "Syötä tuloksia - tarkistussyötteet"
    else:
        otsikko = "Syötä tuloksia"
    sarjat = models.Sarja.objects.filter(kisa__nimi=kisa_nimi)
    taulukko = []
    for s in sarjat:
        tehtavat = s.tehtava_set.all()
        for t in tehtavat:
            t.linkki = "tehtava/" + str(t.id) + "/"
            t.nimi = str(t.jarjestysnro) + ". " + t.nimi
        tehtavat.id = s.id
        tehtavat.otsikko = s.nimi
        taulukko.append(tehtavat)
    return render_to_response("tupa/valitse_linkki.html",
                              {"taulukko": taulukko,
                               "heading": otsikko,
                               "kisa_nimi": kisa_nimi},
                              context_instance=RequestContext(request))


def syotaTehtava(request, kisa_nimi,
                 tehtava_id, talletettu=None, tarkistus=None):
    """
    Määrittää tehtävän syötteet.
    """
    tehtava = get_object_or_404(models.Tehtava, id=tehtava_id)
    osatehtavat = models.OsaTehtava.objects.filter(tehtava=tehtava)
    maaritteet = models.SyoteMaarite.objects.filter(osa_tehtava__tehtava=tehtava)
    tehtava.sarja.laskeTulokset()  # Taustalaskenta

    vartiot = models.Vartio.objects.filter(sarja=tehtava.sarja)
    syoteFormit = []
    posti = None
    syottovirhe = None
    if request.method == "POST":
        posti = request.POST
        if "tarkistettu" in posti.keys():
            tehtava.tarkistettu = True  # Tarkistettu täppä
        else:
            tehtava.tarkistettu = False
    tarkistettu = tehtava.tarkistettu
    validi = True

    tehtavan_syotteet = (models.Syote.objects
                         .filter(maarite__osa_tehtava__tehtava=tehtava))
    if tehtavan_syotteet:
        pass
    tehtava.svirhe = 0
    for v in vartiot:
        rivi = []
        colnum = 0
        for ot in osatehtavat:
            osatehtavan_formit = []
            for m in ot.syotemaarite_set.all():
                maaritteen_syotteet = (tehtavan_syotteet.filter(vartio=v)
                                       .filter(maarite=m))
                m.syotteita = len(maaritteen_syotteet)
                syote = None
                formi = None
                if maaritteen_syotteet:
                    syote = maaritteen_syotteet[0]

                if tarkistus:  # Syötetäänkö tarkistus syötteitä?
                    formi = TarkistusSyoteForm(m, posti,
                                               instance=syote,
                                               prefix=str(v.nro) +
                                               "_" + str(m.pk))
                else:  # Syötetään normi syötteitä.
                    formi = models.SyoteForm(m, posti, instance=syote,
                                      prefix=str(v.nro) + "_" + str(m.pk))
                if "class" not in formi.fields["arvo"].widget.attrs.keys():
                    formi.fields["arvo"].widget.attrs["class"] = "col"
                    formi.fields["arvo"].widget.attrs["class"] += str(colnum)
                else:
                    formi.fields["arvo"].widget.attrs["class"] += " col"
                    formi.fields["arvo"].widget.attrs["class"] += str(colnum)
                if formi.is_valid():  # Talletetaan syöte
                    formi.save()
                else:
                    validi = False
                syote = formi.instance
                if tarkistaVirhe(syote):
                    formi.syottovirhe = "virhe"
                    syottovirhe = "virhe"
                    tehtava.svirhe = 1

                osatehtavan_formit.append(formi)
                colnum += 1
            rivi.append(osatehtavan_formit)
        syoteFormit.append((v, ivi))

    if posti and validi:  # Sivu oikein
        tehtava.save()
        if tarkistus:
            osoite = "/kipa/" + kisa_nimi + "/syota/tarkistus/tehtava/"
            osoite += str(tehtava.id) + "/talletettu/"
            return redirect(osoite)
        else:
            return redirect("/kipa/" + kisa_nimi + "/syota/tehtava/" +
                            str(tehtava.id) + "/talletettu/")
    else:
        tal = ""
        if talletettu == "talletettu" and not posti:
            tal = "Talletettu!"
        tilanne = tehtavanTilanne(tehtava)
        if syottovirhe:
            tilanne = "v"
        syote_url = "/kipa/" + kisa_nimi + "/syota/tehtava/"
        maaritys_url = "/kipa/" + kisa_nimi + "/maarita/tehtava/"
        tulokset_url = "/kipa/" + kisa_nimi
        syote_url += str(tehtava_id) + "/"
        maaritys_url += str(tehtava_id) + "/"
        tulokset_url += "/tulosta/normaali/sarja/" + str(tehtava.sarja.id)
        taa = {"url": "/kipa/" + kisa_nimi + "/syota/",
               "title": u"Syötä tuloksia"}
        return render_to_response("tupa/syota_tehtava.html",
                                  {"tehtava": tehtava,
                                   "sarja": tehtava.sarja.id,
                                   "maaritteet": maaritteet,
                                   "osatehtavat": osatehtavat,
                                   "syotteet": syoteFormit,
                                   "talletettu": tal,
                                   "tilanne": tilanne,
                                   "tarkistettu": tarkistettu,
                                   "kisa_nimi": kisa_nimi,
                                   "tarkistus": tarkistus,
                                   "heading": tehtava.nimi,
                                   "varsinaiset_syotteet_url": syote_url,
                                   "maaritys_url": maarite_url,
                                   "tulokset_url": tulokset_url + "/",
                                   "taakse": taa},
                                  context_instance=RequestContext(request))


def testiTulos(request, kisa_nimi, talletettu=None):
    """
    Määrittää kisalle testitulokset. Eli ns "oikeat" tulokset,
    joita voidaan testeissä verrata laskennan tuottamiin tuloksiin.
    """
    taulukko = []
    sarjat = models.Sarja.objects.filter(kisa__nimi=kisa_nimi)
    taulukko = []
    posti = None
    if request.method == "POST":
        posti = request.POST

    validi = True
    for sarja in sarjat:
        taulut = sarja
        taulut.tiedot = models.Vartio.objects.filter(sarja=sarja)
        taulut.sarja = sarja
        tehtavat = models.Tehtava.objects.filter(sarja=sarja)

        for vartio in taulut.tiedot:
            vartio.tehtavat = tehtavat
            vartio.formit = []
            for tehtava in tehtavat:
                prefix = kisa_nimi + sarja.nimi + tehtava.nimi + vartio.nimi
                formi = models.TestiTulosForm(posti,
                                       vartio,
                                       tehtava,
                                       prefix=prefix)
                if formi.is_valid():
                    formi.save()
                else:
                    validi = False
                v.formit.append(formi)
            taulut.otsikko = s.nimi
            taulut.id = s.id
            taulukko.append(taulut)
    if posti and validi:
        return redirect("/kipa/" + kisa_nimi +
                        "/maarita/testitulos/talletettu/")
    tal = ""
    if talletettu == "talletettu" and not posti:
        tal = "Talletettu!"

    return render_to_response("tupa/testitulos.html",
                              {"taulukko": taulukko,
                               "heading": "Testituloksien määritys",
                               "kisa_nimi": kisa_nimi,
                               "taakse": "/kipa/" + kisa_nimi + "/",
                               "talletettu": tal},
                              context_instance=RequestContext(request))


def tuomarineuvos(request, kisa_nimi, talletettu=None):
    """
    Määrittää kisalle tuomarineuvoston tulokset. Eli tulokset joilla voidaan
    määrittää kiinteät tulokset.
    """
    taulukko = []
    sarjat = models.Sarja.objects.filter(kisa__nimi=kisa_nimi)
    taulukko = []
    posti = None
    if request.method == "POST":
        posti = request.POST

    validi = True
    for sarja in sarjat:
        taulut = sarja
        taulut.tiedot = models.Vartio.objects.filter(sarja=sarja)
        tehtavat = models.Tehtava.objects.filter(sarja=sarja)

        for vartio in taulut.tiedot:
            vartio.tehtavat = tehtavat
            vartio.formit = []
            for tehtava in tehtavat:
                prefix = kisa_nimi + sarja.nimi + tehtava.nimi + vartio + nimi
                formi = TuomarineuvosForm(posti,
                                          vartio,
                                          tehtava,
                                          prefix=prefix)
                if formi.is_valid():
                    formi.save()
                else:
                    validi = False
                vartio.formit.append(formi)
            taulut.otsikko = sarja.nimi
            taulut.id = sarja.id
            taulukko.append(taulut)
            sarja.tulokset()  # Taustalaskenta

    if posti and validi:
        return redirect("/kipa/" + kisa_nimi +
                        "/maarita/tuomarineuvos/talletettu/")
    tal = ""
    if talletettu == "talletettu" and not posti:
        tal = "Talletettu!"
    heading = "Tuomarineuvoston antamien tuloston määritys"
    return render_to_response("tupa/tuomarineuvos.html",
                              {"taulukko": taulukko,
                               "heading": heading,
                               "kisa_nimi": kisa_nimi,
                               "talletettu": tal})


def tulostaSarja(request, kisa_nimi, sarja_id,
                 tulostus=0, vaihtoaika=None, vaihto_id=None):
    """
    models.Sarjan tulokset.
    """
    sarja = models.Sarja.objects.get(id=sarja_id)
    tulokset = sarja.laskeTulokset()
    mukana = tulokset[0]
    ulkona = tulokset[1]
    numero = 1
    for i in range(len(mukana[1:])):
        mukana[i + 1].insert(0, mukana[i + 1][0].tasa + str(numero))
        numero = numero + 1
    for i in range(len(ulkona)):
        ulkona[i].insert(0, lkona[i][0].tasa + str(numero))
        numero = numero + 1
    kisa_aika = sarja.kisa.aika
    kisa_paikka = sarja.kisa.paikka

    templaatti = "tupa/tulokset.html"
    if tulostus:
        templaatti = "tupa/tuloksetHTML.html"
    if vaihtoaika:
        templaatti = "tupa/heijasta.html"
    taakse = {"url": "../../", "title": "Tulokset sarjoittain"}
    return render_to_response(templaatti,
                              {"tulos_taulukko": mukana,
                               "ulkona_taulukko": ulkona,
                               "kisa_nimi": kisa_nimi,
                               "kisa_aika": kisa_aika,
                               "kisa_paikka": kisa_paikka,
                               "heading": sarja.nimi,
                               "vaihtoaika": vaihtoaika,
                               "vaihto_id": vaihto_id,
                               "taakse": taakse},
                              context_instance=RequestContext(request))


def heijasta(request, kisa_nimi, sarja_id=None, tulostus=0):
    kisa = get_object_or_404(Kisa, nimi=kisa_nimi)
    sarjat = kisa.sarja_set.all()
    sarjat = sorted(sarjat, key=lambda sarja: sarja.id)

    if sarja_id is None:
        sarja_id = sarjat[0].id

    sarja_id = int(sarja_id)
    seuraava_id = None
    for index in range(len(sarjat) - 1):
        if sarjat[index].id == sarja_id:
            seuraava_id = sarjat[index + 1].id

    if seuraava_id is None:
        seuraava_id = sarjat[0].id

    return tulostaSarja(request, isa_nimi, sarja_id,
                        vaihtoaika=15, vaihto_id=seuraava_id)


def tulostaSarjaHTML(request, kisa_nimi, sarja_id):
    """
    models.Sarjan tulokset, sivu muotoiltuna tulostusta varten ilman turhia
    grafiikoita.
    """
    return tulostaSarja(request, kisa_nimi, sarja_id, tulostus=1)


def sarjanTuloksetCSV(request, kisa_nimi, sarja_id):
    """
    models.Sarjan tulokset csv tiedostoon esim. Excel-muokkausta varten.
    """
    # Lasketaan tulokset:
    sarja = models.Sarja.objects.get(id=sarja_id)
    tulokset = sarja.laskeTulokset()
    mukana = tulokset[0]
    ulkona = tulokset[1]
    numero = 1
    # Luodaan HttpResponse objekti CSV hederillä.
    response = HttpResponse(mimetype="text/csv")

    disposition = "attachment; filename=" + kisa_nimi
    disposition += "_" + sarja.nimi + ".csv"
    response["Content-Disposition"] = disposition.encode("utf-8")

    writer = UnicodeWriter(response, delimiter=";")
    writer.writerow([sarja.kisa.nimi, "", sarja.nimi])
    # aika
    writer.writerow(["", "", time.strftime("%e.%m.%Y %H:%M ",
                     time.localtime()).replace(".0", ".")])
    writer.writerow([""])  # tyhjä rivi

    otsikkorivi = ["", "Sij", "Nro:", "Vartio:", "Yht:"]
    for teht in mukana[0][2:]:
            otsikkorivi.append(unicode(teht.jarjestysnro))
    writer.writerow(otsikkorivi)

    nimirivi = ["", "", "", "", ""]
    for teht in mukana[0][2:]:
        teht_nimi = teht.nimi
        if teht.lyhenne:
            teht_nimi = teht.lyhenne
        nimirivi.append(teht_nimi)
    writer.writerow(nimirivi)

    pisterivi = ["", "", "Maxpisteet", ""]
    pisteet_yht = 0
    for teht in mukana[0][2:]:
        try:
            if int(teht.maksimipisteet):
                pisteet_yht += int(teht.maksimipisteet)
        except:
            pass
        pisterivi.append(teht.maksimipisteet)
    pisterivi[3] = str(pisteet_yht)
    writer.writerow(pisterivi)
    writer.writerow(["", ""])

    for i in range(len(mukana[1:])):
        vartiorivi = [mukana[i + 1][0].tasa, str(numero),
                      unicode(mukana[i + 1][0].nro),
                      unicode(mukana[i + 1][0].nimi)]
        vartiorivi.append(unicode(mukana[i + 1][1]).replace(".", ","))
        for num in mukana[i + 1][2:]:
            vartiorivi.append(unicode(num).replace(".", ","))
        writer.writerow(vartiorivi)
        numero = numero + 1

    writer.writerow([""])
    writer.writerow(["", "", "Ulkopuolella:"])
    for i in range(len(ulkona)):
        vartiorivi = [ulkona[i][0].tasa, str(numero),
                      unicode(ulkona[i][0].nro), unicode(ulkona[i][0].nimi)]
        vartiorivi.append(unicode(ulkona[i][1]).replace(".", ","))
        for num in ulkona[i][2:]:
            vartiorivi.append(unicode(num).replace(".", ","))
        writer.writerow(vartiorivi)

        ulkona[i].insert(0, umero)
        numero = numero + 1

    sijaluku = u"! = vartion sijaluku laskettu tasapisteissä"
    writer.writerow([""])
    writer.writerow([u"S = syöttämättä"])
    writer.writerow([u"H = vartion suoritus hylätty"])
    writer.writerow([u"K = vartio keskeyttänyt"])
    writer.writerow([u"E = vartio ei ole tehnyt tehtävää"])
    writer.writerow([sijaluku + "määräävien tehtävien perusteella"])
    return response


def piirit(request, isa_nimi):
    """
    Piirikohtaiset tulokset.
    """
    return HttpResponse(kisa_nimi + " PIIRIN TULOSTUS",
                        context_instance=RequestContext(request))


def kopioiTehtavia(request, isa_nimi, sarja_id):
    """
    Valitsee ja kopioi valitut saman kisan tehtävät määriteltyyn sarjaan.
    """
    kisa = get_object_or_404(Kisa, nimi=kisa_nimi)
    sarjaan = get_object_or_404(models.Sarja, id=sarja_id)
    sarjat = models.Sarja.objects.filter(kisa=kisa)
    redirect = True
    posti = None
    if request.method == "POST":
            posti = request.POST

    formit = []
    for s in sarjat:
        vaiht = []
        tehtavat = models.Tehtava.objects.filter(sarja=s)
        for t in tehtavat:
            vaiht.append((t.id, t.nimi))

        class KopioiForm(forms.Form):
            widget = forms.CheckboxSelectMultiple
            kopioitavat_tehtavat = forms.MultipleChoiceField(choices=vaiht,
                                                             widget=widget,
                                                             required=False)
            sarjaForm = KopioiForm(posti, refix=s.nimi)
            formit.append(sarjaForm)
            sarjaForm.otsikko = s.nimi
            sarjaForm.id = s.id

            if posti and sarjaForm.is_valid():
                kopioitavat = sarjaForm.cleaned_data["kopioitavat_tehtavat"]
                for k in kopioitavat:
                    tehtava = get_object_or_404(models.Tehtava, id=k)
                    kopioiTehtava(tehtava, arjaan)
            else:
                redirect = False
    if redirect:
        return redirect("/kipa/" + kisa.nimi + "/maarita/tehtava/")
    else:
        heading = u"Kopioi models.Tehtäviä sarjaan: " + sarjaan.nimi
        taakse = "/kipa/" + kisa_nimi + "/maarita/tehtava/"
        return render_to_response("tupa/valitse_form.html",
                                  {"heading": heading,
                                   "taulukko": formit,
                                   "kisa_nimi": kisa_nimi,
                                   "taakse": taakse,
                                   "napin_tyyppi": "kopioi"},
                                  context_instance=RequestContext(request))


def tallennaKisa(request, kisa_nimi):
    """
    Palauttaa käyttäjälle valitun kisan xml formaatissa.
    Jättää henkilöt ja allergiat tallentamatta.
    """
    kisa = get_object_or_404(Kisa, nimi=kisa_nimi)

    response = HttpResponse(kisa_xml(kisa), mimetype="application/xml")
    response["Content-Disposition"] = "attachment; filename=tietokanta.xml"
    return response


def poistaKisa(request, kisa_nimi):
    kisa = get_object_or_404(Kisa, nimi=kisa_nimi)
    if request.method == "POST":
        kisa.delete()
        return redirect("/kipa/")
    otsikko = "Poista kisa"
    return render_to_response("tupa/poista_kisa.html",
                              {"heading": otsikko, "kisa_nimi": kisa_nimi},
                              context_instance=RequestContext(request))


def saveNewId(object, hangeDict, keyName):
    id = object.id
    object.id = None
    object.save()
    changeDict[keyName][id] = object.id
    return object


def korvaaKisa(request, isa_nimi=None):
    try:
        kisa = models.Kisa.objects.get(nimi=kisa_nimi)
    except:
        kisa = None

    otsikko = u"Korvaa kisa tiedostosta"
    if not kisa_nimi:
        otsikko = u"Lisää kisa tiedostosta "

    form = None
    if request.method == "POST":
        if not kisa_nimi:
            form = UploadFileNameForm(request.POST, request.FILES)
        else:
            form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            if not kisa_nimi:
                kisa_nimi = form.cleaned_data["name"]
                try:
                    kisa = models.Kisa.objects.get(nimi=kisa_nimi)
                except:
                    kisa = None

            xml = r""
            for chunk in request.FILES["file"].chunks():
                    xml += chunk

            kisat = []
            sarjat = []
            vartiot = []
            tehtavat = []
            testaustulokset = []
            tuomarit = []
            osatehtavat = []
            maaritteet = []
            syotteet = []
            parametrit = []

            for obj in serializers.deserialize("xml", xml):
                if type(obj.object) == models.Kisa:
                    kisat.append(obj.object)
                elif type(obj.object) == models.Sarja:
                    sarjat.append(obj.object)
                elif type(obj.object) == models.Vartio:
                    vartiot.append(obj.object)
                elif type(obj.object) == models.Tehtava:
                    tehtavat.append(obj.object)
                elif type(obj.object) == models.TestausTulos:
                    testaustulokset.append(obj.object)
                elif type(obj.object) == TuomarineuvosTulos:
                    tuomarit.append(obj.object)
                elif type(obj.object) == models.OsaTehtava:
                    osatehtavat.append(obj.object)
                elif type(obj.object) == models.SyoteMaarite:
                    maaritteet.append(obj.object)
                elif type(obj.object) == models.Syote:
                    syotteet.append(obj.object)
                elif type(obj.object) == models.Parametri:
                    parametrit.append(obj.object)

            translations = {"kisat": {},
                            "sarjat": {},
                            "vartiot": {},
                            "tehtavat": {},
                            "testaustulokset": {},
                            "tuomarit": {},
                            "osatehtavat": {},
                            "maaritteet": {},
                            "syotteet": {},
                            "parametrit": {}}

            if not len(kisat) == 1:
                return redirect("/kipa/" + kisa_nimi + "/korvaa/")
            elif kisa:
                kisa.delete()
            kisat[0].nimi = kisa_nimi
            saveNewId(kisat[0], translations, "kisat")
            for sarja in sarjat:
                sarja.kisa_id = translations["kisat"][sarja.kisa_id]
                saveNewId(sarja, translations, "sarjat")
            for vartio in vartiot:
                vartio.sarja_id = translations["sarjat"][vartio.sarja_id]
                saveNewId(vartio, translations, "vartiot")
            for tehtava in tehtavat:
                tehtava.sarja_id = translations["sarjat"][tehtava.sarja_id]
                saveNewId(tehtava, translations, "tehtavat")
            for testi in testaustulokset:
                testi.tehtava_id = translations["tehtavat"][testi.tehtava_id]
                testi.vartio_id = translations["vartiot"][testi.vartio_id]
                saveNewId(testi, translations, "testaustulokset")
            for tuomari in tuomarit:
                translaatio = translations["tehtavat"][tuomari.tehtava_id]
                tuomari.tehtava_id = translaatio
                tuomari.vartio_id = translations["vartiot"][tuomari.vartio_id]
                saveNewId(tuomari, translations, "tuomarit")
            for oosatehtava in osatehtavat:
                translaatio = translations["tehtavat"][osatehtava.tehtava_id]
                osatehtava.tehtava_id = translaatio
                saveNewId(osatehtava, translations, "osatehtavat")
            for m in maaritteet:
                translaatio = translations["osatehtavat"][m.osa_tehtava_id]
                m.osa_tehtava_id = translaatio
                saveNewId(m, translations, "maaritteet")
            for s in syotteet:
                s.maarite_id = translations["maaritteet"][s.maarite_id]
                s.vartio_id = translations["vartiot"][s.vartio_id]
                saveNewId(s, translations, "syotteet")
            for p in parametrit:
                translaatio = translations["osatehtavat"][p.osa_tehtava_id]
                p.osa_tehtava_id = translaatio
                saveNewId(p, translations, "parametrit")

            return redirect("/kipa/" + kisa_nimi + "/")
    else:
        if not kisa_nimi:
                form = UploadFileNameForm()
        else:
            form = UploadFileForm()

    if kisa_nimi:
        return render_to_response("tupa/upload.html",
                                  {"heading": otsikko,
                                   "form": form,
                                   "kisa_nimi": kisa_nimi},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response("tupa/upload_riisuttu.html",
                                  {"heading": otsikko,
                                   "form": form,
                                   "kisa_nimi": kisa_nimi},
                                  context_instance=RequestContext(request))


def post_txt(request, arametrit):
    """
    Apunäkymä virhetilanteisiin. (error 500, erver internal error)
    -Luo kisan tietokannan xml formaattiin ja lisää perään post_data:n
    testausta varten.
    -Palauttaa xml tiedoston.
    """
    from xml.dom.minidom import parseString
    kisa_nimi = re.search(r"^osoite=/kipa/(\w+)/", arametrit).group(1)
    kisa = get_object_or_404(Kisa, nimi=kisa_nimi)
    test_data = kisa_xml(kisa)
    post_data = parametrit.split("&")
    doc = parseString(test_data)
    post_test = doc.createElement("post_request")
    post_test.setAttribute("address", post_data[0].split("=")[1])

    for p in post_data[1:]:
        data = p.split("=")
        elem = doc.createElement("input")
        elem.setAttribute("name", data[0])
        elem.setAttribute("value", data[1])
        post_test.appendChild(elem)
    doc.childNodes[0].appendChild(post_test)

    response = HttpResponse(doc.toprettyxml(indent="  "),
                            mimetype="application/xml",
                            context_instance=RequestContext(request))
    response["Content-Disposition"] = "attachment; filename=tietokanta.xml"
    return response


def raportti_500(request):
    """
    Html Error 500 sivu (Server internal error),
    Suomeksi: kipa vaan todennäköisesti kaatui.
    -Sisältää linkin joka palauttaa tietokannan,
    sekä viimeisimmän post datan xml formaatissa testausta varten.
    """
    linkki = SafeText("<a href=/kipa")
    linkki += "/> #00000000" + str(random.uniform(1, 10)) + "</a>"
    return render_to_response("500.html",
                              {"error": SafeText(linkki)},
                              context_instance=RequestContext(request))


def haeTulos(tuloksetSarjalle, vartio, tehtava):
    # Mukana olevat
    sarjanTulokset = tuloksetSarjalle[0]
    for vart_nro in range(1, en(sarjanTulokset)):
        for teht_nro in range(2, en(sarjanTulokset[vart_nro])):
            tul = sarjanTulokset[vart_nro][teht_nro]
            va = sarjanTulokset[vart_nro][0]
            if va == vartio and sarjanTulokset[0][teht_nro] == tehtava:
                return tul
    # Ulkopuoliset
    for vart_nro in range(0, en(tuloksetSarjalle[1])):
        for teht_nro in range(2, en(tuloksetSarjalle[1][vart_nro])):
            tul = tuloksetSarjalle[1][vart_nro][teht_nro]
            va = tuloksetSarjalle[1][vart_nro][0]
            if va == vartio and tuloksetSarjalle[0][0][teht_nro] == tehtava:
                return tul


def luoTestiTulokset(request, isa_nimi, sarja_id):
    """
    Luo testitulokset valitulle sarjalle ja tallentaa ne kantaan
    """
    sarja = get_object_or_404(models.Sarja, id=sarja_id)
    tulokset = sarja.laskeTulokset()

    for t in sarja.tehtava_set.all():
            for v in sarja.vartio_set.all():
                    tulos = haeTulos(tulokset, v, t)
                    tt = models.TestausTulos.objects.get_or_create(vartio=v,
                                                            tehtava=t)
                    tt.pisteet = str(tulos)
                    tt.save()
    return redirect("/kipa/" + kisa_nimi + "/maarita/testitulos/")


def laskennanTilanne(request, isa_nimi):
    kisa = get_object_or_404(Kisa, nimi=kisa_nimi)
    taulukko = [[]]
    taulukko[0].append((0, "Tehtava"))

    suurin = 0
    # Otsikkorivi
    for s in kisa.sarja_set.all():
            taulukko[0].append((None, s.nimi))
            for t in s.tehtava_set.all():
                    if t.jarjestysnro > suurin:
                        suurin = t.jarjestysnro

    # Luodaan taulukko
    for i in range(suurin):
            rivi = [(0, +1)]
            for s in kisa.sarja_set.all():
                    rivi.append("")
            taulukko.append(rivi)
    rivi = [(0, "valmiina")]
    for s in kisa.sarja_set.all():
            rivi.append("")

    taulukko.append(rivi)
    sarake = 1
    for s in kisa.sarja_set.all():
        vartioita = s.vartio_set.all().count()
        syotteita = 0
        kesk_syotteita = 0
        for t in s.tehtava_set.all():
            taulukko[t.jarjestysnro][sarake] = tehtavanTilanne(t)
            syotteita += (models.Syote.objects.filter(maarite__osa_tehtava__tehtava=t)
                          .exclude(arvo="kesk").count())
            kesk_syotteita += (models.Syote.objects
                               .filter(maarite__osa_tehtava__tehtava=t)
                               .filter(arvo="kesk").count())

            if(t.svirhe):
                taulukko[t.jarjestysnro][sarake] = ("v", t.nimi)

        maaritteita = (models.SyoteMaarite.objects
                       .filter(osa_tehtava__tehtava__sarja=s).count())
        if syotteita > 0 and maaritteita > 0:
            prosentit = (Decimal(syotteita * 100) /
                         (maaritteita * vartioita - kesk_syotteita))
            prosentit = prosentit.quantize(Decimal("1."), rounding=ROUND_UP)
            taulukko[suurin + 1][sarake] = (None, tr(prosentit) + " %")
        else:
            taulukko[suurin + 1][sarake] = (None, "0 %")
        sarake += 1

    return render_to_response("tupa/laskennan_tilanne.html",
                              {"taulukko": taulukko,
                               "kisa_nimi": kisa_nimi,
                               "heading": "Laskennan tilanne"},
                              context_instance=RequestContext(request))


def apua(request):
    """
    Apua onnettomalle ja surulliselle käyttäjälle
    """
    return redirect("/kipamedia/manual_v02.pdf")


def tehtavanVaiheet(request, isa_nimi, tehtava_id, vartio_id=None):
    # kisa = get_object_or_404(Kisa, nimi=kisa_nimi )
    tehtava = get_object_or_404(models.Tehtava, id=tehtava_id)
    vartiot = models.Vartio.objects.filter(sarja=tehtava.sarja)
    if not len(vartiot):
        responssi = "<html><body><h1>Ei vartioita</h1><br></body></html>"
        responssi += "<a href='/kipa/lista/maarita/tehtava/" + str(tehtava_id)
        responssi += "/'>" + u"Takaisin määrittelyyn </a> <br><br>"
        responssi += "</body></html>"
        return HttpResponse(responssi)

    # vartio = vartiot[0]
    if vartio_id == "":
        vartio_id = str(tehtava.sarja.vartio_set.all()[0].id)
        get_object_or_404(Vartio, id=vartio_id)
    tehtava = get_object_or_404(models.Tehtava, id=tehtava_id)

    responssi = u"<html><body>Vartion laskennan vaiheet tehtävässä "
    responssi += tehtava.nimi + " <br> "
    enableLogging()
    clearLoki()
    tehtavan_syotteet = (models.Syote.objects
                         .filter(maarite__osa_tehtava__tehtava=tehtava))
    if tehtavan_syotteet:
        pass
    laskeSarja(tehtava.sarja, tehtavan_syotteet,
               models.Vartio.objects.filter(id=vartio_id), [tehtava])
    responssi += "<a href='/kipa/lista/maarita/tehtava/" + str(tehtava_id)
    responssi += "/>" + "Takaisin määrittelyyn </a> <br><br>"
    for v in vartiot:
        responssi += "<a href='/kipa/" + kisa_nimi + "/maarita/vaiheet/"
        responssi += str(tehtava_id) + "/" + str(v.id) + "'/>"
        responssi += str(v.nro) + " " + v.nimi + "</a> &nbsp; &nbsp;"
    responssi += palautaLoki()
    responssi += "</body></html>"
    return HttpResponse(responssi)
