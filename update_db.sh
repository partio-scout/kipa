#!/bin/bash

rm -r fixtures/old.xml
echo Kopioidaan data tiedostoon fixtures/old.xml
python manage.py dumpdata --format=xml > fixtures/old.xml
echo Luodaan uuden tietokannan malli tupa/tietokata.dia tiedostosta models.py tiedostoon.
python tupa/dia2django.py tupa/tietokanta.dia tupa/models.py
echo Nollataan ja päivitetään tietokantataulut.
python manage.py reset --noinput tupa
echo Ladataan fixturen data uuteen tietokantaan.
python manage.py loaddata fixture fixtures/old.xml

