@echo off
cd /d %~dp0
rem -r fixtures\old.xml
echo Luodaan legacy datamalli legacy/models.py
..\python\python.exe manage.py inspectlegacy
echo Kopioidaan vanha data tiedostoon fixtures/old.xml
..\python\python.exe manage.py dumpdata tupa --format=xml --indent=4 > fixtures\old.xml
..\python\python.exe legacy\RenameFixture.py 
echo Luodaan uuden tietokannan malli tupa\tietokata.dia tiedostosta models.py tiedostoon.
..\python\python.exe tupa\dia2django.py tupa/tietokanta.dia tupa/models.py
echo Nollataan ja p‰ivitet‰‰n tietokantataulut.
..\python\python.exe manage.py reset --noinput tupa
echo Ladataan fixturen data uuteen tietokantaan.
..\python\python.exe manage.py loaddata fixture fixtures/old.xml
echo Luodaan tietokantataulu tuloscachelle:
..\python\python.exe manage.py createcachetable tupa_tulos_cache
echo Valmis!
pause


